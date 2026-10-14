import math
import random
import tkinter as tk

FPS = 60

class SpaceArenaGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Star Fighter AI Arena")

        # Configure Fullscreen Mode
        self.is_fullscreen = True
        self.root.attributes("-fullscreen", True)

        # Get Screen Dimensions
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()

        # Canvas
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="#080a10", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Stars Background
        self.stars = [(random.randint(0, self.width), random.randint(0, self.height), random.randint(1, 3)) for _ in range(120)]

        # Game State
        self.difficulty = "MEDIUM"
        self.game_over = False
        self.winner = ""

        # Player Fighter
        self.px, self.py = 200, self.height // 2
        self.p_vx, self.p_vy = 0, 0
        self.php, self.pmax_hp = 100, 100
        self.penergy, self.pmax_energy = 100, 100
        self.p_angle = 0

        # AI Fighter
        self.aix, self.aiy = self.width - 200, self.height // 2
        self.ai_vx, self.ai_vy = 0, 0
        self.ai_hp, self.ai_max_hp = 120, 120
        self.ai_energy, self.ai_max_energy = 100, 100
        self.ai_angle = 0
        self.ai_fire_cooldown = 0

        # Projectiles & Particles
        self.lasers = []      # [x, y, vx, vy, is_player, color, life]
        self.particles = []   # [x, y, vx, vy, color, life, size]
        self.damage_popups = []

        # Input Handling
        self.keys = {}
        self.mx, self.my = self.width // 2, self.height // 2

        self.root.bind("<KeyPress>", self.key_down)
        self.root.bind("<KeyRelease>", self.key_up)
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)
        self.canvas.bind("<Motion>", self.mouse_move)
        self.canvas.bind("<Button-1>", self.mouse_click)

        # Main Loop
        self.loop()

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)

    def exit_fullscreen(self, event=None):
        self.is_fullscreen = False
        self.root.attributes("-fullscreen", False)

    def key_down(self, event):
        k = event.keysym.lower()
        self.keys[k] = True
        if k == '1':
            self.difficulty = "BEGINNER"
        elif k == '2':
            self.difficulty = "MEDIUM"
        elif k == '3':
            self.difficulty = "LEGEND"
        elif k == 'r':
            self.reset_game()

    def key_up(self, event):
        self.keys[event.keysym.lower()] = False

    def mouse_move(self, event):
        self.mx, self.my = event.x, event.y

    def mouse_click(self, event):
        if not self.game_over and self.penergy >= 10:
            self.fire_laser(is_player=True)
            self.penergy -= 10

    def fire_laser(self, is_player):
        if is_player:
            angle = self.p_angle
            speed = 13
            lx = self.px + math.cos(angle) * 22
            ly = self.py + math.sin(angle) * 22
            color = "#00f0ff"
        else:
            angle = self.ai_angle
            speed = 10 if self.difficulty == "BEGINNER" else 12 if self.difficulty == "MEDIUM" else 14
            lx = self.aix + math.cos(angle) * 22
            ly = self.aiy + math.sin(angle) * 22
            color = "#ff3355"

        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        self.lasers.append([lx, ly, vx, vy, is_player, color, 80])

    def reset_game(self):
        self.px, self.py = 200, self.height // 2
        self.p_vx, self.p_vy = 0, 0
        self.php, self.penergy = 100, 100
        self.aix, self.aiy = self.width - 200, self.height // 2
        self.ai_vx, self.ai_vy = 0, 0
        self.ai_hp, self.ai_energy = 120, 100
        self.game_over = False
        self.lasers.clear()
        self.particles.clear()
        self.damage_popups.clear()

    def update_ai(self):
        if self.game_over:
            return

        dx = self.px - self.aix
        dy = self.py - self.aiy
        dist = math.hypot(dx, dy)

        # AI Aiming & Predictive Lead Targeting
        if self.difficulty == "LEGEND":
            time_to_hit = dist / 14.0
            pred_x = self.px + self.p_vx * time_to_hit
            pred_y = self.py + self.p_vy * time_to_hit
            target_angle = math.atan2(pred_y - self.aiy, pred_x - self.aix)
        elif self.difficulty == "MEDIUM":
            target_angle = math.atan2(dy, dx) + random.uniform(-0.1, 0.1)
        else:  # BEGINNER
            target_angle = math.atan2(dy, dx) + random.uniform(-0.35, 0.35)

        self.ai_angle = target_angle

        # AI Movement & Dodging Behavior
        speed = 2.0 if self.difficulty == "BEGINNER" else 3.8 if self.difficulty == "MEDIUM" else 5.2
        
        dodged = False
        if self.difficulty == "LEGEND":
            for l in self.lasers:
                if l[4]:  # Player laser
                    ldist = math.hypot(l[0] - self.aix, l[1] - self.aiy)
                    if ldist < 140:
                        perp_angle = self.ai_angle + math.pi / 2
                        self.ai_vx += math.cos(perp_angle) * 1.8
                        self.ai_vy += math.sin(perp_angle) * 1.8
                        dodged = True
                        break

        if not dodged:
            if dist > 260:
                self.ai_vx += math.cos(target_angle) * (speed * 0.1)
                self.ai_vy += math.sin(target_angle) * (speed * 0.1)
            elif dist < 140:
                self.ai_vx -= math.cos(target_angle) * (speed * 0.1)
                self.ai_vy -= math.sin(target_angle) * (speed * 0.1)

        # Physics & Friction
        self.ai_vx *= 0.94
        self.ai_vy *= 0.94
        self.aix += self.ai_vx
        self.aiy += self.ai_vy

        # Clamp Bounds
        self.aix = max(40, min(self.width - 40, self.aix))
        self.aiy = max(40, min(self.height - 40, self.aiy))

        # AI Firing Logic
        if self.ai_fire_cooldown > 0:
            self.ai_fire_cooldown -= 1
        else:
            if dist < 550:
                fire_chance = 0.03 if self.difficulty == "BEGINNER" else 0.08 if self.difficulty == "MEDIUM" else 0.18
                if random.random() < fire_chance and self.ai_energy >= 10:
                    self.fire_laser(is_player=False)
                    self.ai_energy -= 10
                    self.ai_fire_cooldown = 16 if self.difficulty == "LEGEND" else 26

    def create_explosion(self, x, y, color, count=18):
        for _ in range(count):
            vx = random.uniform(-5, 5)
            vy = random.uniform(-5, 5)
            size = random.randint(2, 6)
            self.particles.append([x, y, vx, vy, color, 35, size])

    def update(self):
        if not self.game_over:
            # Player Steering & Acceleration
            self.p_angle = math.atan2(self.my - self.py, self.mx - self.px)

            accel = 0.45
            if self.keys.get('shift') and self.penergy > 5:
                accel = 0.9
                self.penergy -= 0.6
                tx = self.px - math.cos(self.p_angle) * 16
                ty = self.py - math.sin(self.p_angle) * 16
                self.particles.append([tx, ty, random.uniform(-1, 1), random.uniform(-1, 1), "#00f0ff", 14, 3])

            if self.keys.get('w'):
                self.p_vx += math.cos(self.p_angle) * accel
                self.p_vy += math.sin(self.p_angle) * accel
            if self.keys.get('s'):
                self.p_vx -= math.cos(self.p_angle) * (accel * 0.5)
                self.p_vy -= math.sin(self.p_angle) * (accel * 0.5)
            if self.keys.get('a'):
                self.p_vx += math.cos(self.p_angle - math.pi/2) * (accel * 0.6)
                self.p_vy += math.sin(self.p_angle - math.pi/2) * (accel * 0.6)
            if self.keys.get('d'):
                self.p_vx += math.cos(self.p_angle + math.pi/2) * (accel * 0.6)
                self.p_vy += math.sin(self.p_angle + math.pi/2) * (accel * 0.6)

            # Apply Physics
            self.p_vx *= 0.93
            self.p_vy *= 0.93
            self.px += self.p_vx
            self.py += self.p_vy

            self.px = max(40, min(self.width - 40, self.px))
            self.py = max(40, min(self.height - 40, self.py))

            # Recharge
            self.penergy = min(100, self.penergy + 0.35)
            self.ai_energy = min(100, self.ai_energy + 0.35)

            self.update_ai()

            # Projectiles & Hit Detection
            for l in self.lasers[:]:
                l[0] += l[2]
                l[1] += l[3]
                l[6] -= 1

                # Player Hit
                if not l[4]:
                    if math.hypot(l[0] - self.px, l[1] - self.py) < 22:
                        dmg = random.randint(12, 18)
                        self.php = max(0, self.php - dmg)
                        self.damage_popups.append([self.px, self.py - 15, f"-{dmg}", "#ff3355", 25])
                        self.create_explosion(l[0], l[1], "#ff3355", count=8)
                        if l in self.lasers: self.lasers.remove(l)
                        continue

                # AI Hit
                if l[4]:
                    if math.hypot(l[0] - self.aix, l[1] - self.aiy) < 24:
                        dmg = random.randint(15, 22)
                        self.ai_hp = max(0, self.ai_hp - dmg)
                        self.damage_popups.append([self.aix, self.aiy - 15, f"-{dmg}", "#00f0ff", 25])
                        self.create_explosion(l[0], l[1], "#00f0ff", count=8)
                        if l in self.lasers: self.lasers.remove(l)
                        continue

                if l[6] <= 0 or l[0] < 0 or l[0] > self.width or l[1] < 0 or l[1] > self.height:
                    if l in self.lasers: self.lasers.remove(l)

            # Game Over Conditions
            if self.php <= 0:
                self.game_over = True
                self.winner = f"AI BOSS ({self.difficulty}) DESTROYED YOU!"
                self.create_explosion(self.px, self.py, "#00f0ff", count=45)
            elif self.ai_hp <= 0:
                self.game_over = True
                self.winner = "VICTORY! AI BOSS DESTROYED!"
                self.create_explosion(self.aix, self.aiy, "#ff3355", count=45)

    def draw(self):
        self.canvas.delete("all")

        # Stars Background
        for s in self.stars:
            self.canvas.create_rectangle(s[0], s[1], s[0]+s[2], s[1]+s[2], fill="#3a4454", outline="")

        # Border
        self.canvas.create_rectangle(15, 15, self.width - 15, self.height - 15, outline="#1e293b", width=3)

        # Particles
        for p in self.particles[:]:
            p[0] += p[2]
            p[1] += p[3]
            p[5] -= 1
            self.canvas.create_oval(p[0]-p[6], p[1]-p[6], p[0]+p[6], p[1]+p[6], fill=p[4], outline="")
            if p[5] <= 0:
                self.particles.remove(p)

        # Lasers
        for l in self.lasers:
            tail_x = l[0] - l[2] * 1.2
            tail_y = l[1] - l[3] * 1.2
            self.canvas.create_line(l[0], l[1], tail_x, tail_y, fill=l[5], width=3)

        # Player Ship
        pa = self.p_angle
        p1 = (self.px + math.cos(pa) * 22, self.py + math.sin(pa) * 22)
        p2 = (self.px + math.cos(pa + 2.5) * 16, self.py + math.sin(pa + 2.5) * 16)
        p3 = (self.px + math.cos(pa - 2.5) * 16, self.py + math.sin(pa - 2.5) * 16)
        self.canvas.create_polygon([p1, p2, p3], fill="#00f0ff", outline="#ffffff", width=2)

        # AI Boss Ship
        aia = self.ai_angle
        a1 = (self.aix + math.cos(aia) * 25, self.aiy + math.sin(aia) * 25)
        a2 = (self.aix + math.cos(aia + 2.3) * 18, self.aiy + math.sin(aia + 2.3) * 18)
        a3 = (self.aix + math.cos(aia - 2.3) * 18, self.aiy + math.sin(aia - 2.3) * 18)
        self.canvas.create_polygon([a1, a2, a3], fill="#ff3355", outline="#ffffff", width=2)

        # Damage Popups
        for d in self.damage_popups[:]:
            self.canvas.create_text(d[0], d[1], text=d[2], fill=d[3], font=("Consolas", 12, "bold"))
            d[1] -= 0.8
            d[4] -= 1
            if d[4] <= 0:
                self.damage_popups.remove(d)

        # HUD Header Panel
        diff_col = "#2ecc71" if self.difficulty == "BEGINNER" else "#f1c40f" if self.difficulty == "MEDIUM" else "#e74c3c"
        self.canvas.create_text(160, 40, text=f"AI MODE: {self.difficulty}", fill=diff_col, font=("Consolas", 14, "bold"))
        self.canvas.create_text(self.width // 2, 40, text="[W,A,S,D]: Fly | [SHIFT]: Boost | [CLICK]: Fire | [1,2,3]: Difficulty | [F11]: Toggle Fullscreen | [ESC]: Windowed | [R]: Reset", fill="#64748b", font=("Consolas", 11))

        # Health & Energy Bars
        # Player (Bottom Left)
        self.canvas.create_rectangle(50, self.height - 50, 250, self.height - 35, fill="#1e293b", outline="")
        self.canvas.create_rectangle(50, self.height - 50, 50 + (self.php / self.pmax_hp * 200), self.height - 35, fill="#00f0ff", outline="")
        self.canvas.create_text(150, self.height - 58, text=f"PLAYER SHIELD: {int(self.php)}", fill="#ffffff", font=("Consolas", 10, "bold"))

        self.canvas.create_rectangle(50, self.height - 25, 250, self.height - 16, fill="#1e293b", outline="")
        self.canvas.create_rectangle(50, self.height - 25, 50 + (self.penergy / self.pmax_energy * 200), self.height - 16, fill="#3b82f6", outline="")

        # AI Boss (Bottom Right)
        self.canvas.create_rectangle(self.width - 250, self.height - 50, self.width - 50, self.height - 35, fill="#1e293b", outline="")
        self.canvas.create_rectangle(self.width - 250, self.height - 50, self.width - 250 + (self.ai_hp / self.ai_max_hp * 200), self.height - 35, fill="#ff3355", outline="")
        self.canvas.create_text(self.width - 150, self.height - 58, text=f"AI BOSS HULL: {int(self.ai_hp)}", fill="#ffffff", font=("Consolas", 10, "bold"))

        # Game Over Screen Overlay
        if self.game_over:
            self.canvas.create_rectangle(0, 0, self.width, self.height, fill="#000000", stipple="gray50")
            self.canvas.create_text(self.width // 2, self.height // 2 - 20, text=self.winner, fill="#f1c40f", font=("Impact", 34))
            self.canvas.create_text(self.width // 2, self.height // 2 + 30, text="Press 'R' to Restart | Press '1', '2', or '3' to change difficulty", fill="#ffffff", font=("Consolas", 13))

    def loop(self):
        self.update()
        self.draw()
        self.root.after(1000 // FPS, self.loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = SpaceArenaGame(root)
    root.mainloop()