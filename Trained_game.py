import pygame
import pickle
import numpy as np
import random
from Training_game import Game, WIDTH, HEIGHT, MAX_POWER, RIM_Y, WHITE, BLACK, BALL_RADIUS
import random
import math

class AutoGame(Game):
    def __init__(self):
        super().__init__()
        self.load_models()
        self.shot_delay = 1000
        self.last_shot_time = 0
        
    def load_models(self):
        with open('angle_model.pkl', 'rb') as f:
            self.angle_model = pickle.load(f)
        with open('speed_model.pkl', 'rb') as f:
            self.speed_model = pickle.load(f)
    
    def auto_shoot(self):
        rim_x = np.array([[self.rim_x]])
        predicted_angle = self.angle_model.predict(rim_x)[0]
        predicted_speed = self.speed_model.predict(rim_x)[0]
        
        self.arrow_speed = predicted_speed
        self.arrow_angle = np.radians(predicted_angle)
        self.trajectory = self.calculate_trajectory(self.arrow_speed, self.arrow_angle, self.arrow_x, self.arrow_y)
        self.arrow_in_motion = True
        self.basket_scored_this_chance = False
        self.prev_positions = []
        self.last_bounce_time = 0
        
    def run(self):
        running = True
        while running:
            self.screen.blit(self.background_image, (0, 0))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            current_time = pygame.time.get_ticks()
            if not self.arrow_in_motion and current_time - self.last_shot_time >= self.shot_delay:
                self.auto_shoot()
                self.last_shot_time = current_time

            ball_rect = self.ball_image.get_rect()
            ball_rect.centerx = int(self.arrow_x)
            ball_rect.centery = int(self.arrow_y)
            self.screen.blit(self.ball_image, ball_rect)

            hoop_rect = self.hoop_image.get_rect()
            hoop_rect.centerx = self.rim_x
            hoop_rect.centery = RIM_Y + 25
            self.screen.blit(self.hoop_image, hoop_rect)

            if self.arrow_in_motion and self.trajectory:
                prev_x, prev_y = self.arrow_x, self.arrow_y
                self.arrow_x, self.arrow_y = self.trajectory.pop(0)
                
                dx = self.arrow_x - prev_x
                dy = self.arrow_y - prev_y
                current_speed = math.hypot(dx, dy)
                current_time = pygame.time.get_ticks()

                if current_time - self.last_bounce_time > 50:
                    rim_collision, collision_type = self.check_rim_collision(prev_x, prev_y, self.arrow_x, self.arrow_y)
                    if rim_collision:
                        self.last_bounce_time = current_time
                        bounce_speed = current_speed * 0.1

                        if collision_type in ["front_left", "front_right", "back"]:
                            bounce_angle = math.pi - math.atan2(-dy, dx)
                            bounce_angle += 0.1 if bounce_angle > 0 else -0.1
                        self.trajectory = self.calculate_trajectory(bounce_speed * 60, bounce_angle, self.arrow_x, self.arrow_y)

                    elif self.check_backboard_collision(prev_x, prev_y, self.arrow_x, self.arrow_y):
                        self.last_bounce_time = current_time
                        bounce_speed = current_speed * 0.1
                        bounce_angle = math.pi - math.atan2(-dy, dx)
                        self.trajectory = self.calculate_trajectory(bounce_speed * 60, bounce_angle, self.arrow_x, self.arrow_y)

                self.check_basket_score(self.arrow_x, self.arrow_y)

                if not self.trajectory or self.arrow_y >= HEIGHT:
                    self.arrow_in_motion = False
                    self.trajectory = []
                    self.arrow_x, self.arrow_y = 100, HEIGHT - 100
                    self.chances_played += 1
                    self.rim_x = random.randint(200, WIDTH - 200)
                    
                    if self.chances_played >= 15:
                        if not self.show_game_over_screen():
                            running = False

            self.display_stats()
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()

    def display_stats(self):
        chances_text = self.font.render(f"Chances: {self.chances_played} / 15", True, WHITE)
        score_text = self.font.render(f"Baskets Scored: {self.baskets_scored} / 15", True, WHITE)
        fps_text = self.font.render(f"FPS: {int(self.clock.get_fps())}", True, WHITE)
        
        self.screen.blit(chances_text, (10, 10))
        self.screen.blit(score_text, (10, 50))
        self.screen.blit(fps_text, (10, 90))

if __name__ == "__main__":
    game = AutoGame()
    game.run()