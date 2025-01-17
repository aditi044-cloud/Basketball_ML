import pygame
import math
import random
import csv
import os
import time
import pickle

WIDTH, HEIGHT = 800, 600
BALL_RADIUS = 20
RIM_RADIUS = 40
RIM_THICKNESS = 5
RIM_HEIGHT = 42
GRAVITY = 17
POWER_SCALING = 0.8
MAX_POWER = 105
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BACKBOARD_WIDTH = 15
BACKBOARD_HEIGHT = 100
RIM_Y = HEIGHT - 300
RIM_OFFSET = 35
RIM_VERTICAL_OFFSET = 20

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

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Basketball Game")
        self.font = pygame.font.SysFont(None, 36)
        self.clock = pygame.time.Clock()

        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.hoop_image = pygame.image.load(os.path.join(script_dir, 'hoop.png'))
        self.ball_image = pygame.image.load(os.path.join(script_dir, 'ball.png'))
        self.background_image = pygame.image.load(os.path.join(script_dir, 'background.png'))
        
        self.hoop_image = pygame.transform.scale(self.hoop_image, (150, 150))
        self.ball_image = pygame.transform.scale(self.ball_image, (BALL_RADIUS * 2, BALL_RADIUS * 2))
        self.background_image = pygame.transform.scale(self.background_image, (WIDTH, HEIGHT))

        self.total_energy = 0
        self.avg_energy = 0
        
        self.shot_data = []
        self.reset_game()

    def check_rim_collision(self, prev_x, prev_y, ball_x, ball_y):
        rim_left_x = self.rim_x - RIM_RADIUS
        rim_right_x = self.rim_x + RIM_RADIUS
        back_rim_x = self.rim_x + RIM_RADIUS + RIM_OFFSET
        rim_collision_y = RIM_Y + RIM_VERTICAL_OFFSET
        
        moving_right = ball_x > prev_x
        moving_left = ball_x < prev_x

        if rim_collision_y <= ball_y <= rim_collision_y + RIM_HEIGHT * 2:
            if (moving_right and 
                abs(ball_x - rim_left_x) <= BALL_RADIUS and
                rim_collision_y <= ball_y <= rim_collision_y + RIM_HEIGHT * 2):
                return True, "front_left"
            
            if (moving_left and 
                abs(ball_x - rim_right_x) <= BALL_RADIUS and
                rim_collision_y <= ball_y <= rim_collision_y + RIM_HEIGHT * 2):
                return True, "front_right"
            
            if (moving_left and
                abs(ball_x - back_rim_x) <= BALL_RADIUS and
                rim_collision_y <= ball_y <= rim_collision_y + RIM_HEIGHT * 2):
                return True, "back"
        return False, None

    def check_backboard_collision(self, prev_x, prev_y, ball_x, ball_y):
        BACKBOARD_COLLISION_OFFSET = 35
        backboard_x = self.rim_x + RIM_RADIUS + RIM_OFFSET - BACKBOARD_COLLISION_OFFSET
        backboard_y = RIM_Y - BACKBOARD_HEIGHT // 2

        BACKBOARD_EXTENSION = 50
        moving_right = ball_x > prev_x
        if (
            moving_right and
            prev_x <= backboard_x <= ball_x + BALL_RADIUS and
            backboard_y <= ball_y <= backboard_y + BACKBOARD_HEIGHT + BACKBOARD_EXTENSION
        ):
            return True
        return False

    def reset_game(self):
        self.chances_played = 0
        self.baskets_scored = 0
        self.arrow_x, self.arrow_y = 100, HEIGHT - 100
        self.dragging = False
        self.trajectory = []
        self.arrow_speed = 0
        self.arrow_angle = 0
        self.arrow_in_motion = False
        self.basket_scored_this_chance = False
        self.rim_x = random.randint(200, WIDTH - 200)
        self.game_over = False
        self.prev_positions = []
        self.last_bounce_time = 0
        self.shot_data = []

    def calculate_trajectory(self, speed, angle, start_x, start_y):
        trajectory = []
        time = 0
        while True:
            time += 1 / 10
            x = start_x + speed * math.cos(angle) * time
            y = start_y - (speed * math.sin(angle) * time - 0.5 * GRAVITY * time ** 2)
            if y >= HEIGHT or x < 0 or x > WIDTH:
                break
            trajectory.append((x, y))
        return trajectory

    def check_basket_score(self, ball_x, ball_y):
        if not self.basket_scored_this_chance:
            rim_left_x = self.rim_x - RIM_RADIUS
            rim_right_x = self.rim_x + RIM_RADIUS
            rim_collision_y = RIM_Y + RIM_VERTICAL_OFFSET
            
            self.prev_positions.append((ball_x, ball_y))
            if len(self.prev_positions) > 5:
                self.prev_positions.pop(0)

            if len(self.prev_positions) >= 2:
                prev_y = self.prev_positions[-2][1]
                
                if (rim_left_x + BALL_RADIUS < ball_x < rim_right_x - BALL_RADIUS and
                    rim_collision_y < ball_y < rim_collision_y + RIM_HEIGHT * 2 and
                    prev_y < ball_y):
                    
                    if ball_y > rim_collision_y + RIM_HEIGHT - BALL_RADIUS:
                        self.basket_scored_this_chance = True
                        self.baskets_scored += 1
                        return True
            return False

    def export_shot_data(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, 'data.csv')
        file_exists = os.path.isfile(csv_path)
        with open(csv_path, 'a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['Speed', 'Angle', 'Rim_Center_X'])
            for shot in self.shot_data:
                writer.writerow(shot)

    def show_game_over_screen(self):
        self.export_shot_data()
        
        play_again_btn = Button(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50, "Play Again", (0, 100, 0))
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if play_again_btn.handle_event(event):
                    self.reset_game()
                    return True

            self.screen.fill(BLACK)
            game_over_text = self.font.render("Game Over!", True, WHITE)
            score_text = self.font.render(f"Baskets Scored: {self.baskets_scored} / 15", True, WHITE)
            
            self.screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
            self.screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
            play_again_btn.draw(self.screen, self.font)
            
            pygame.display.flip()

    def run(self):
        running = True
        
        while running:
            fps = self.clock.get_fps()
            
            self.screen.blit(self.background_image, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if math.hypot(event.pos[0] - self.arrow_x, event.pos[1] - self.arrow_y) <= BALL_RADIUS:
                        self.dragging = True

                if event.type == pygame.MOUSEBUTTONUP:
                    if self.dragging:
                        self.dragging = False
                        dx, dy = self.arrow_x - event.pos[0], self.arrow_y - event.pos[1]
                        raw_speed = math.hypot(dx, dy) * POWER_SCALING
                        self.arrow_speed = min(raw_speed, MAX_POWER)
                        self.arrow_angle = math.atan2(-dy, dx)
                        self.trajectory = self.calculate_trajectory(self.arrow_speed, self.arrow_angle, self.arrow_x, self.arrow_y)
                        self.shot_data.append([self.arrow_speed, math.degrees(self.arrow_angle), self.rim_x])
                        self.arrow_in_motion = True
                        self.basket_scored_this_chance = False
                        self.prev_positions = []
                        self.last_bounce_time = 0

            ball_rect = self.ball_image.get_rect()
            ball_rect.centerx = int(self.arrow_x)
            ball_rect.centery = int(self.arrow_y)
            self.screen.blit(self.ball_image, ball_rect)

            hoop_rect = self.hoop_image.get_rect()
            hoop_rect.centerx = self.rim_x
            hoop_rect.centery = RIM_Y + 25
            self.screen.blit(self.hoop_image, hoop_rect)

            if not self.arrow_in_motion and self.trajectory:
                for point in self.trajectory:
                    pygame.draw.circle(self.screen, WHITE, (int(point[0]), int(point[1])), 2)

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

            chances_text = self.font.render(f"Chances: {self.chances_played} / 15", True, WHITE)
            self.screen.blit(chances_text, (10, 10))
            score_text = self.font.render(f"Baskets Scored: {self.baskets_scored} / 15", True, WHITE)
            self.screen.blit(score_text, (10, 50))
            fps_text = self.font.render(f"FPS: {int(fps)}", True, WHITE)
            self.screen.blit(fps_text, (10, 90))
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()