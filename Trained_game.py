import pygame
import pickle
import numpy as np
import random
import math
from Training_game import Game, WIDTH, HEIGHT, MAX_POWER, RIM_Y, WHITE, BLACK, BALL_RADIUS, RIM_RADIUS, RIM_VERTICAL_OFFSET, RIM_HEIGHT

# Define the Button class
class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.is_hovered = False

    def draw(self, screen, font):
        color = (min(self.color[0] + 30, 255), min(self.color[1] + 30, 255), min(self.color[2] + 30, 255)) if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class AutoGame(Game):
    def __init__(self):
        super().__init__()
        self.load_models()
        self.shot_delay = 1000
        self.last_shot_time = 0
        self.arrow_x2 = WIDTH - 100
        self.arrow_y2 = HEIGHT - 100
        self.arrow_in_motion2 = False
        self.trajectory2 = []
        self.basket_scored_this_chance2 = False
        self.prev_positions2 = []
        self.last_bounce_time2 = 0
        self.baskets_scored_left = 0
        self.baskets_scored_right = 0
        self.player_left_name = None
        self.player_right_name = None

    def load_models(self):
        left_model_file = 'modell.pkl'
        with open(left_model_file, 'rb') as f:
            model_data = pickle.load(f)
            self.model_l = model_data['model']
            self.poly_l = model_data['poly']
        self.player_left_name = left_model_file.split('.')[0]

        right_model_file = 'modelr.pkl'
        with open(right_model_file, 'rb') as f:
            model_data = pickle.load(f)
            self.model_r = model_data['model']
            self.poly_r = model_data['poly']
        self.player_right_name = right_model_file.split('.')[0]

    def auto_shoot(self):
        rim_x = np.array([[self.rim_x]])
        X_poly = self.poly_l.transform(rim_x)
        predictions = self.model_l.predict(X_poly)[0]
        predicted_speed, predicted_angle = predictions
        self.arrow_speed = predicted_speed
        self.arrow_angle = np.radians(predicted_angle)
        self.trajectory = self.calculate_trajectory(self.arrow_speed, self.arrow_angle, self.arrow_x, self.arrow_y)
        self.arrow_in_motion = True
        self.basket_scored_this_chance = False
        self.prev_positions = []
        self.last_bounce_time = 0
        X_poly = self.poly_r.transform(rim_x)
        predictions = self.model_r.predict(X_poly)[0]
        predicted_speed, predicted_angle = predictions
        self.arrow_speed2 = predicted_speed
        self.arrow_angle2 = np.radians(180 - predicted_angle)
        self.trajectory2 = self.calculate_trajectory(self.arrow_speed2, self.arrow_angle2, self.arrow_x2, self.arrow_y2)
        self.arrow_in_motion2 = True
        self.basket_scored_this_chance2 = False
        self.prev_positions2 = []
        self.last_bounce_time2 = 0

    def check_rim_collision(self, prev_x, prev_y, ball_x, ball_y):
        rim_left_x = self.rim_x - RIM_RADIUS + 10
        rim_right_x = self.rim_x + RIM_RADIUS + 4
        rim_collision_y = RIM_Y + RIM_VERTICAL_OFFSET
        moving_right = ball_x > prev_x
        moving_left = ball_x < prev_x
        moving_down = ball_y > prev_y
        if (rim_left_x <= ball_x <= rim_right_x and 
            abs(ball_y - rim_collision_y) <= BALL_RADIUS and 
            moving_down):
            if ball_x < self.rim_x:
                return True, "top_left"
            else:
                return True, "top_right"
        if rim_collision_y <= ball_y <= rim_collision_y + RIM_HEIGHT * 2:
            if (abs(ball_x - rim_left_x) <= BALL_RADIUS):
                if moving_right:
                    return True, "front_left"
                elif moving_left:
                    return True, "back_left"
            if (abs(ball_x - rim_right_x) <= BALL_RADIUS):
                if moving_left:
                    return True, "front_right"
                elif moving_right:
                    return True, "back_right"
        return False, None

    def check_ball_collision(self):
        if self.arrow_in_motion and self.arrow_in_motion2:
            dx = self.arrow_x2 - self.arrow_x
            dy = self.arrow_y2 - self.arrow_y
            distance = math.hypot(dx, dy)
            
            if distance <= BALL_RADIUS * 2:
                collision_angle = math.atan2(dy, dx)
                
                if self.trajectory and self.trajectory2:
                    dx1 = self.trajectory[0][0] - self.arrow_x
                    dy1 = self.trajectory[0][1] - self.arrow_y
                    speed1 = math.hypot(dx1, dy1)
                    dx2 = self.trajectory2[0][0] - self.arrow_x2
                    dy2 = self.trajectory2[0][1] - self.arrow_y2
                    speed2 = math.hypot(dx2, dy2)
                    bounce_speed1 = speed2 * 0.15
                    bounce_speed2 = speed1 * 0.15
                    self.trajectory = self.calculate_trajectory(
                        bounce_speed1 * 60,
                        collision_angle + math.pi,
                        self.arrow_x,
                        self.arrow_y
                    )
                    self.trajectory2 = self.calculate_trajectory(
                        bounce_speed2 * 60,
                        collision_angle,
                        self.arrow_x2,
                        self.arrow_y2
                    )

    def show_game_over_screen(self):
        # Create a larger font for the game over screen
        game_over_font = pygame.font.SysFont(None, 72)
        stats_font = pygame.font.SysFont(None, 48)
        button_font = pygame.font.SysFont(None, 36)

        # Create the "Play Again" button
        play_again_btn = Button(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 50, "Play Again", (0, 100, 0))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if play_again_btn.handle_event(event):
                    self.reset_game()
                    return True

            # Draw the game over screen
            self.screen.fill(BLACK)

            # Display "Game Over!" text
            game_over_text = game_over_font.render("Game Over!", True, WHITE)
            self.screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 150))

            # Display player names and scores
            left_player_text = stats_font.render(f"{self.player_left_name}: {self.baskets_scored_left}", True, WHITE)
            right_player_text = stats_font.render(f"{self.player_right_name}: {self.baskets_scored_right}", True, WHITE)
            self.screen.blit(left_player_text, (WIDTH // 2 - left_player_text.get_width() // 2, HEIGHT // 2 - 50))
            self.screen.blit(right_player_text, (WIDTH // 2 - right_player_text.get_width() // 2, HEIGHT // 2))

            # Draw the "Play Again" button
            play_again_btn.draw(self.screen, button_font)

            pygame.display.flip()

    def run(self):
        running = True
        while running:
            self.screen.blit(self.background_image, (0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            current_time = pygame.time.get_ticks()
            if not self.arrow_in_motion and not self.arrow_in_motion2 and current_time - self.last_shot_time >= self.shot_delay:
                self.auto_shoot()
                self.last_shot_time = current_time
            ball_rect = self.ball_image.get_rect()
            ball_rect.centerx = int(self.arrow_x)
            ball_rect.centery = int(self.arrow_y)
            self.screen.blit(self.ball_image, ball_rect)
            ball_rect2 = self.ball_image.get_rect()
            ball_rect2.centerx = int(self.arrow_x2)
            ball_rect2.centery = int(self.arrow_y2)
            self.screen.blit(self.ball_image, ball_rect2)
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
                        bounce_speed = current_speed * 0.15
                        if collision_type in ["front_left", "front_right"]:
                            bounce_angle = math.pi - math.atan2(-dy, dx)
                            bounce_angle += 0.1 if bounce_angle > 0 else -0.1
                        elif collision_type in ["top_left", "top_right"]:
                            bounce_angle = -math.atan2(dy, dx)
                            bounce_angle += 0.2 if collision_type == "top_right" else -0.2
                        self.trajectory = self.calculate_trajectory(bounce_speed * 60, bounce_angle, self.arrow_x, self.arrow_y)
                if self.check_basket_score(self.arrow_x, self.arrow_y):
                    self.baskets_scored_left += 1
                if not self.trajectory or self.arrow_y >= HEIGHT:
                    self.arrow_in_motion = False
                    self.trajectory = []
            if self.arrow_in_motion2 and self.trajectory2:
                prev_x2, prev_y2 = self.arrow_x2, self.arrow_y2
                self.arrow_x2, self.arrow_y2 = self.trajectory2.pop(0)
                dx2 = self.arrow_x2 - prev_x2
                dy2 = self.arrow_y2 - prev_y2
                current_speed2 = math.hypot(dx2, dy2)
                current_time = pygame.time.get_ticks()
                if current_time - self.last_bounce_time2 > 50:
                    rim_collision2, collision_type2 = self.check_rim_collision(prev_x2, prev_y2, self.arrow_x2, self.arrow_y2)
                    if rim_collision2:
                        self.last_bounce_time2 = current_time
                        bounce_speed2 = current_speed2 * 0.15
                        if collision_type2 in ["front_left", "front_right"]:
                            bounce_angle2 = math.pi - math.atan2(-dy2, dx2)
                            bounce_angle2 += 0.1 if bounce_angle2 > 0 else -0.1
                        elif collision_type2 in ["top_left", "top_right"]:
                            bounce_angle2 = -math.atan2(dy2, dx2)
                            bounce_angle2 += 0.2 if collision_type2 == "top_right" else -0.2
                        self.trajectory2 = self.calculate_trajectory(bounce_speed2 * 60, bounce_angle2, self.arrow_x2, self.arrow_y2)
                if self.check_basket_score(self.arrow_x2, self.arrow_y2):
                    self.baskets_scored_right += 1
                if not self.trajectory2 or self.arrow_y2 >= HEIGHT:
                    self.arrow_in_motion2 = False
                    self.trajectory2 = []
            self.check_ball_collision()
            if not self.arrow_in_motion and not self.arrow_in_motion2:
                self.arrow_x, self.arrow_y = 100, HEIGHT - 100
                self.arrow_x2, self.arrow_y2 = WIDTH - 100, HEIGHT - 100
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
        score_left_text = self.font.render(f"Left Baskets: {self.baskets_scored_left}", True, WHITE)
        score_right_text = self.font.render(f"Right Baskets: {self.baskets_scored_right}", True, WHITE)
        fps_text = self.font.render(f"FPS: {int(self.clock.get_fps())}", True, WHITE)
        self.screen.blit(chances_text, (10, 10))
        self.screen.blit(score_left_text, (10, 50))
        self.screen.blit(score_right_text, (10, 90))
        self.screen.blit(fps_text, (10, 130))

if __name__ == "__main__":
    game = AutoGame()
    game.run()