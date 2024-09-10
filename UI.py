import pygame
import math
import random

class Game:
        
    def __init__(self):

        pygame.init()
        self.running = True
        self.game_over = False
        self.fps = 60
        self.fps_clock = pygame.time.Clock()
        self.menu = True
        self.main_menu = True
        self.screen_ratio = (16,9)
        self.ai = False
        
        self.start_game_sound=pygame.mixer.Sound('res/sounds/startup_sound.mp3')
        self.start_game_sound.set_volume(0.5)

        
        
        self.play_startup_sound()

        self._setup_screen()
        self._setup_elements()
        self._setup_audio()
        self._setup_fonts()
        self._setup_menu()
                    
    class Player(pygame.sprite.Sprite):
        
        def __init__(self, screen, scale, fps = 120, facing_left = False):

            # Call the parent class (Sprite) constructor
            pygame.sprite.Sprite.__init__(self)

            self.screen = screen
            self.scale = scale
            self.fps = fps
            self.ground = round(self.screen.get_height()*0.78)

            # sprites
            self.sprite = pygame.image.load('res/images/player_1.png').convert_alpha()
            self.sprite = pygame.transform.scale(self.sprite, self.scale((50,50)))
            self.rect = self.sprite.get_rect()

            self.sword_sprite = pygame.image.load('res/images/sword.png').convert_alpha()
            self.sword_sprite = pygame.transform.scale(self.sword_sprite, self.scale((75,30)))
            self.sword_rect = self.sword_sprite.get_rect()
            
            self.downstrike_sprite = pygame.transform.rotate(self.sword_sprite,-90)
            self.downstrike_rect = self.downstrike_sprite.get_rect()

            self.shield_sprite = pygame.image.load('res/images/shield.png').convert_alpha()
            self.shield_sprite = pygame.transform.scale(self.shield_sprite, self.scale((5,50)))
            self.shield_rect = self.shield_sprite.get_rect()
            
            # positioninge
            self.rect.left = self.scale(100)
            self.rect.bottom = self.ground
            self.X_change = 0
            self.Y_change = 0
            self.speed = self.scale(8)

            # jumping
            self.jumping = False
            self.jump_speed = self.scale([0,0,-20,-50,-50,-30,-15,-5,-5,-2,-2,0,0,0,0])
            self.jump_fps_time = len(self.jump_speed)
            self.jump_counter = self.jump_fps_time

            # falling
            self.falling = False
            self.fall_ticker = 0
            self.initial_fall_speed = self.scale(3)
            self.on_top = False

            # dashing
            self.most_recent_press = False
            self.press_state = 0
            self.press_time = .1
            self.press_timer = 0
            self.dashing = False
            self.dash_mod = -1
            self.dash_speed = self.scale([0,-30,-30,-30,-30,-30,-30])
            self.dash_fps_time = len(self.dash_speed) 
            self.dash_counter = self.dash_fps_time

            # knockback
            self.knockback = False
            self.knockback_time = .125
            self.knockback_counter = self.knockback_time*self.fps
            self.knockback_speed = self.scale(15)
            
            # striking
            self.sword_hurtbox = False
            self.striking = False
            
            self.sword_time = .2
            self.sword_fps_time = self.sword_time*self.fps
            self.sword_come_out_time = self.sword_fps_time - .02*self.fps
            self.sword_come_in_time = .08*self.fps
            
            self.sword_offsetx = self.scale(50)
            self.sword_offsety = self.scale(-10)
            self.sword_rect.x = self.rect.x+self.sword_offsetx
            self.sword_rect.y = self.rect.y-self.sword_offsety

            # downstrike
            self.downstriking = False
            self.downstrike_offsetx = self.scale(10)
            self.downstrike_offsety = self.scale(-30)
            self.downstrike_rect.x = self.rect.x+self.downstrike_offsetx
            self.downstrike_rect.y = self.rect.y-self.downstrike_offsety
            self.land_downstrike_stun_time_long = 30
            self.land_downstrike_stun_time_short = 5
            self.land_downstrike_stun = False

            # shield
            self.shield_offsetx = self.scale(50)
            self.shield_offsety = 0
            self.shield_rect.x = self.rect.x+self.shield_offsetx
            self.shield_rect.y = self.rect.y-self.shield_offsety
            self.shielding = False
            self.shield_block = False
            self.shield_time = .24
            self.shield_fps_time = self.shield_time*self.fps

            # stamina
            self.max_stamina = 5
            self.stamina = 5
            self.stamina_reload_time = .4
            self.stamina_reload_counter = self.stamina_reload_time*self.fps

            # other attributes
            self.life = 5
            self.invinsible = False
            self.i_frames = 60
            self.i_frames_invinsible = True

            # sounds
            self.shield_sound = pygame.mixer.Sound('res/sounds/shield.mp3')
            self.sword_swoosh_sound = pygame.mixer.Sound('res/sounds/sword_swoosh.wav')
            self.sword_hit_ground_sound = pygame.mixer.Sound('res/sounds/sword_hit_ground.wav')
            self.jump_sound = pygame.mixer.Sound('res/sounds/jump.mp3')
            self.land_sound = pygame.mixer.Sound('res/sounds/land.mp3')
            self.dash_sound = pygame.mixer.Sound('res/sounds/dash.mp3')

            # input keys
            self.input_dict = {
                'jump': pygame.K_w,
                'left': pygame.K_a,
                'right': pygame.K_d,
                'down': pygame.K_s,
                'sword': pygame.K_f,
                'shield': pygame.K_g
            }

            self.facing_left = facing_left
            if self.facing_left is True:
                self.sprite = pygame.image.load('res/images/player_2.png').convert_alpha()
                self.sprite = pygame.transform.scale(self.sprite, self.scale((50,50)))
                self.flip_player()
                self.rect.right = self.screen.get_width()-self.scale(100)
                self.input_dict = {
                    'jump': pygame.K_UP,
                    'left': pygame.K_LEFT,
                    'right': pygame.K_RIGHT,
                    'down': pygame.K_DOWN,
                    'sword': pygame.K_k,
                    'shield': pygame.K_l
                }
        
        def show(self):
            '''Show character sprite.'''

            self.screen.blit(self.sprite, (self.rect.x, self.rect.y))

        def update(self):
            '''Handle events that must take place every frame.'''

      
            self.continue_knockback()  # for ai player actually to continue after a hit
            self.continue_dash()
            self.continue_jump()
            self.check_fall()
            self.continue_fall()
            self.stamina_update()
            self.continue_strike()
            self.continue_downstrike()
            self.continue_land_downstrike()
            self.continue_shield()
            self.continue_iframes()
            self.iterate_dash_timer()

        def movement(self):
            '''Handle sprite movements.'''

            self.rect.move_ip(self.X_change,self.Y_change)

            if self.rect.x <= 0:
                self.rect.x = 0
            elif self.rect.right >= self.screen.get_width():
                self.rect.right = self.screen.get_width()       

            if self.rect.bottom > self.ground:
                self.rect.bottom = self.ground

        def flip_player(self):
            
            self.sprite = pygame.transform.flip(self.sprite, True, False)
            self.sword_sprite = pygame.transform.flip(self.sword_sprite, True, False)
            self.shield_sprite = pygame.transform.flip(self.shield_sprite, True, False)
            self.sword_offsetx = (self.sword_offsetx+self.scale(25))*-1
            self.shield_offsetx = (self.shield_offsetx-self.scale(45))*-1
            self.dash_mod *= -1

        def check_fall(self):

            if (self.rect.bottom < self.ground) & (self.jumping is False) & (self.on_top is False):
                self.deploy_fall()

        def deploy_fall(self):
            
            if self.falling is False:
                self.falling = True
                self.fall_ticker = 1

        def continue_fall(self):

            if (self.rect.bottom == self.ground) or (self.on_top is True):
                self.falling = False
                if self.Y_change >= 0:
                    self.Y_change = 0

            if self.falling is True:
                if self.fall_ticker < 10:
                    self.fall_ticker += 1
                self.Y_change = self.initial_fall_speed*self.fall_ticker

        def deploy_jump(self):
            
            if (self.jumping is False) & (self.falling is False):
                
                self.jumping = True
                self.jump_counter = self.jump_fps_time
                self.jump_sound.play()
                
        def continue_jump(self):

            if self.jumping is True:
                if self.jump_counter <= 0:
                    self.jumping = False
                else:
                    timer = int(self.jump_fps_time - self.jump_counter)
                    self.Y_change = self.jump_speed[timer]
                    self.jump_counter -= 1

        def deploy_knockback(self):
            
            if self.knockback is False:
                self.knockback = True
                self.X_change = self.knockback_speed
                self.knockback_counter = self.knockback_time*self.fps
        
        def continue_knockback(self):

            if self.knockback is True:
                self.knockback_counter -= 1
                
                if self.knockback_counter <= 0:
                    self.knockback = False
                    self.X_change = 0
                else:
                    self.X_change = self.knockback_speed
        
        def check_dash(self, press=None):
            
            # if something is pressed
            if press is not None:
                # if ready
                if self.press_state == 0:
                    # get ready to look for upkey
                    self.press_state +=1
                    # start timer
                    self.press_timer = self.press_time*self.fps
                    # set press id
                    self.most_recent_press = press
                # if down up down within timer
                if (self.press_state == 2):
                    # if within timer window
                    if self.press_timer > 0:
                        # if press equals first press
                        if self.most_recent_press == press:
                            self.deploy_dash()
                    # always restart after stage 2
                    self.press_state = 0
                # if(self.press_state==1 and press == self.most_recent_press):
                #     self.press_state +=1
                #     self.most_recent_press = press
            # if nothing is pressed and press_state is ready for upkey
            if (press is None) & (self.press_state == 1):
                self.press_state += 1
            #if timer is up, return to state 0
            if self.press_timer == 0:
                self.press_state = 0

        def iterate_dash_timer(self):

            if self.press_timer > 0:
                self.press_timer -= 1

        def deploy_dash(self):

            if (self.is_acting() is False) & (self.stamina > 0):
                self.X_change = self.dash_speed[0]*self.dash_mod
                self.dash_counter = self.dash_fps_time
                self.dashing = True
                self.dash_sound.play()

                self.stamina -= 1
                self.stamina_reload_counter = self.stamina_reload_time*self.fps
        
        def continue_dash(self):
            
            if self.dashing is True:
                if self.dash_counter <= 0:
                    self.dashing = False
                    self.X_change = 0
                else:
                    timer = int(self.dash_fps_time - self.dash_counter)
                    self.X_change = self.dash_speed[timer]*self.dash_mod
                    self.dash_counter -= 1

        def stamina_update(self):
            if (self.stamina < self.max_stamina) & (self.jumping is False):
                self.stamina_reload_counter -= 1
                if self.stamina_reload_counter <= 0:
                    self.stamina += 1
                    self.stamina_reload_counter = self.stamina_reload_time*self.fps 
        
        def deploy_strike(self):
            '''Deploys sword strike and starts timer.'''

            if (self.is_acting() is False) & (self.stamina > 0):
                self.sword_swoosh_sound.play()
                self.striking = True
                self.striking_counter = self.sword_fps_time
                
                self.stamina -= 1
                self.stamina_reload_counter = self.stamina_reload_time*self.fps
                
        def continue_strike(self):
            '''Handles sword strike including sprite, frozen frames, and timer countdown'''

            if self.striking is True:

                self.striking_counter -= 1

                if self.sword_come_in_time < self.striking_counter < self.sword_come_out_time:
                    self.screen.blit(self.sword_sprite, (self.rect.x+self.sword_offsetx, self.rect.y-self.sword_offsety))
                    self.sword_rect.x = self.rect.x+self.sword_offsetx
                    self.sword_rect.y = self.rect.y-self.sword_offsety
                    self.sword_hurtbox = True
                else:
                    self.sword_hurtbox = False
                
                if self.striking_counter <= 0:
                    self.striking = False

        def deploy_downstrike(self):

            if (self.is_acting() is False) & (self.stamina > 0):
                if (self.jumping) or (self.falling):
                    self.X_change = 0
                    self.jumping = False
                    self.sword_swoosh_sound.play()
                    self.downstriking = True
                    
                    self.stamina -= 1
                    self.stamina_reload_counter = self.stamina_reload_time*self.fps

        def continue_downstrike(self):

            if self.downstriking is True:

                if self.falling is True:
                    self.X_change = 0
                    self.screen.blit(self.downstrike_sprite, (self.rect.x+self.downstrike_offsetx, self.rect.y-self.downstrike_offsety))
                    self.downstrike_rect.x = self.rect.x+self.downstrike_offsetx
                    self.downstrike_rect.y = self.rect.y-self.downstrike_offsety
                
                else:
                    self.downstriking = False
                    
                    if self.on_top is True: 
                        self.deploy_land_downstrike(self.land_downstrike_stun_time_short)
                    else:
                        self.deploy_land_downstrike(self.land_downstrike_stun_time_long)

        def deploy_land_downstrike(self, timer):
            self.sword_hit_ground_sound.play()
            self.land_downstrike_stun = True
            self.land_downstrike_timer = timer
            self.X_change = 0
        
        def continue_land_downstrike(self):

            if self.land_downstrike_stun is True:
                if self.land_downstrike_timer > 0:
                    self.land_downstrike_timer -= 1
                else:
                    self.land_downstrike_stun = False

        def deploy_shield(self):
            
            if (self.is_acting() is False) & (self.stamina > 0):
                self.shield_sound.play()
                self.shielding = True
                self.shield_counter = self.shield_fps_time
                
                self.stamina -= 1
                self.stamina_reload_counter = self.stamina_reload_time*self.fps
                
                self.X_change = 0
        
        def continue_shield(self):

            if self.shielding is True:

                self.shield_counter -= 1
                self.screen.blit(self.shield_sprite, (self.rect.x+self.shield_offsetx, self.rect.y-self.shield_offsety))
                self.shield_rect.x = self.rect.x+self.shield_offsetx
                self.shield_rect.y = self.rect.y-self.shield_offsety
                self.shield_block = True
                
                if self.shield_counter <= 0:
                    self.shielding = False
                    self.shield_block = False

        def deploy_iframes(self):

            self.invinsible = True
            self.i_frames_invinsible = True
            self.i_frames = 60

        def continue_iframes(self):
            '''Handles counting down invinsibility frames.'''
            
            if self.i_frames_invinsible is True: 
                self.i_frames -= 1
                if self.i_frames <= 0:
                    self.invinsible = False
                    self.i_frames_invinsible = False
                    self.i_frames = 60
        
        def take_hit(self, knockback = True):
            self.life -= 1
            if knockback is True:
                self.deploy_knockback()
            self.deploy_iframes()
            
        def is_ready(self):
            '''Returns True if player is ready for new inputs.'''
            if (self.knockback is False) & (self.land_downstrike_stun is False):
                return True
            return False
        
        def is_acting(self):

            if (self.striking is True) or (self.downstriking is True) or (self.shielding is True) or (self.dashing is True):
                return True
            return False

    class AIEnemy():
        
        def __init__(
            self, 
            input_dict,
            playera,
            playerb):

            # self.ai_scheme = ai_scheme
            self.playera = playera
            self.playerb = playerb
            self.ai_scheme= None
            self.depth=4
            self.actions = ['left', 'right', 'jump', 'down', 'sword', 'shield']
            


            self.input_dict = input_dict
            self.ai_key_dict = {
                self.input_dict['jump']:0,
                self.input_dict['left']:0,
                self.input_dict['right']:0,
                self.input_dict['down']:0,
                self.input_dict['sword']:0,
                self.input_dict['shield']:0}
            
            

            self.walk_left = [self.input_dict['left']]*10
            self.walk_right = [self.input_dict['right']]*10
            self.sword = [self.input_dict['sword']]
            self.shield = [self.input_dict['shield']]
            self.dash_left = [self.input_dict['left']]*3 + [None]*3 + [self.input_dict['left']]*5 + self.sword
            self.dash_right = [self.input_dict['right']]*3 + [None]*3 + [self.input_dict['right']]*5 + self.sword
            self.jump_left = [[self.input_dict['jump'],self.input_dict['left']]] + self.walk_left
            self.jump_right = [[self.input_dict['jump'],self.input_dict['right']]] + self.walk_right
            self.jump_left_downstrike = self.jump_left + self.walk_left*2 + [self.input_dict['down']]
            self.jump_right_downstrike = self.jump_right + self.walk_right*2 + [self.input_dict['down']]
            self.down_strike = [self.input_dict['jump']]*5 + [self.input_dict['down']]

            self.sequence_index = 0
            self.sequence_list = [
                self.walk_left, 
                self.walk_right,
                self.dash_left,
                self.dash_right,
                self.sword, self.sword, self.sword,
                self.shield, self.shield, self.shield,
                self.jump_left_downstrike,
                self.jump_right_downstrike,
                self.down_strike
            ]
            self.sequence = self.walk_left
            self.sequence_break = False
            self.avoiding = False
            
            
        def set_level(self, level):
            self.ai_scheme=level 
            
        def get_input(self):
            if self.ai_scheme == 'easy':
               return self._genetic_algorithm_input()
            elif self.ai_scheme == 'medium':
               return self._alpha_beta_input()
            elif self.ai_scheme == 'hard':
               return self._heuristics()




        #heurestic ** KEEP IT , but can make A* based on it !!
        def _heuristics(self):

            self._check_sequence_break()

            if self.sequence_index >= len(self.sequence)-1:
                self.sequence = self._choose_heuristic()
                if self.sequence_break is True:
                    self.sequence_break = False
                self.sequence_index = 0
            else:
                self.sequence_index += 1

            input = self.sequence[self.sequence_index]
            ai_key_dict_copy = self.ai_key_dict.copy()
            
            if not isinstance(input,list):
                input = [input]
            for i in input:
                ai_key_dict_copy[i] = 1
            
            return ai_key_dict_copy

        def _choose_heuristic(self):

            sequence = [None]
            # no stamina
            if not self._has_stamina():
                sequence = self._avoid()
            # is over or under
            elif self._is_on_top():
                possible_sequences = [self.down_strike,self.walk_right,self.walk_left] 
                sequence = random.sample(possible_sequences,1)[0]
            elif self._is_under():
                if self._has_stamina(3):
                    possible_sequences = [self.dash_left,self.dash_right,self.walk_left*2,self.walk_right*2]
                    sequence = random.sample(possible_sequences,1)[0]
                else:
                    possible_sequences = [self.walk_left*2,self.walk_right*2]
                    sequence = random.sample(possible_sequences,1)[0]
            # far away
            elif self._is_far():
                if self._is_left():
                    sequence = self.walk_left
                else:
                    sequence = self.walk_right
            # close
            elif self._is_close():
                if self.playera.striking:
                    sequence = self.shield
                else:
                    if self._is_left():
                        sequence = [[self.input_dict['left'],self.input_dict['sword']]]
                    else:
                        sequence = [[self.input_dict['right'],self.input_dict['sword']]]
                if self.playerb.striking:
                    if self._is_left:
                        sequence = self.walk_left
                    if self._is_right:
                        sequence = self.walk_right
            # medium distance
            elif self._is_left() & self._is_medium():
                if self._has_stamina(2):
                    possible_sequences = [self.jump_left_downstrike,self.dash_left,self.walk_left]
                    sequence = random.sample(possible_sequences,1)[0]
                else:
                    possible_sequences = [self.jump_left_downstrike,self.walk_left]
                    sequence = random.sample(possible_sequences,1)[0]
            elif self._is_right() & self._is_medium():
                if self._has_stamina(2):
                    possible_sequences = [self.jump_right_downstrike,self.dash_right,self.walk_right]
                    sequence = random.sample(possible_sequences,1)[0]
                else:
                    possible_sequences = [self.jump_right_downstrike,self.walk_right]
                    sequence = random.sample(possible_sequences,1)[0]
            # enemy in stun
            elif self._is_left() & (self.playera.land_downstrike_stun is True):
                if self._is_far() & self._has_stamina(3):
                    possible_sequences = [self.walk_left,self.dash_left]
                    sequence = random.sample(possible_sequences,1)[0]
                if (self._is_medium() or self._is_close()) & self._has_stamina(1):
                    sequence = self.walk_left + self.sword
            elif self._is_right() & (self.playera.land_downstrike_stun is True):
                if self._is_far() & self._has_stamina(3):
                    possible_sequences = [self.walk_right,self.dash_right]
                    sequence = random.sample(possible_sequences,1)[0]
                if (self._is_medium() or self._is_close()) & self._has_stamina(1):
                    sequence = self.walk_right + self.sword
            
            return sequence
        
        
        def _check_sequence_break(self):
            
            if self.sequence_break is False:
                
                if self._is_close() & self._has_stamina() & self.playera.striking:
                    self._do_sequence_break(self.shield)
        
        def _do_sequence_break(self, sequence):

            self.sequence_index = 0
            self.sequence_break = True
            self.sequence = sequence

        def _avoid(self):
            
            self.sequence_index = 0
            self.sequence_break = True
            self.avoiding = True
            if self.playerb.stamina >=2:
                self.avoiding = False

            if self._is_left():
                if self._near_right_edge():
                    possible_sequences = [self.walk_left*3,self.jump_left]
                    sequence = random.sample(possible_sequences,1)[0] 
                    return sequence
                else:
                    self.walk_left
            if self._is_right():
                if self._near_left_edge():
                    possible_sequences = [self.walk_right*3,self.jump_right]
                    sequence = random.sample(possible_sequences,1)[0] 
                    return sequence
                else:
                    self.walk_right
            return [None]
           
        def _is_left(self):
            return self.playera.rect.centerx < self.playerb.rect.centerx

        def _is_right(self):
             return self.playera.rect.centerx > self.playerb.rect.centerx
            
        def _is_far(self, distance = 160):
            return abs(self.playera.rect.centerx - self.playerb.rect.centerx) > self.playera.scale(distance)
        
        def _is_medium(self, low_distance = 100, high_distance = 160):
            return (not self._is_far(high_distance)) & (not self._is_close(low_distance))
        
        def _is_close(self, distance = 100):
            return abs(self.playera.rect.centerx - self.playerb.rect.centerx) < self.playera.scale(distance)

        def _is_on_top(self):
            return (self.playerb.rect.centery < self.playera.rect.centery) & self._is_close(20)
        
        def _is_under(self):
            return (self.playerb.rect.centery > self.playera.rect.centery) & self._is_close(50)

        def _near_right_edge(self):
            return abs(self.playerb.rect.x - self.playerb.screen.get_width()) < self.playera.scale(100)
        
        def _near_left_edge(self):
            return abs(self.playerb.rect.x - 0) < self.playera.scale(100)
        
        def _has_stamina(self, min = 1):
            return self.playerb.stamina >= min
        
        
        #AlphA_BETA Pruning !!
        
        def evaluate_state(self):
            score = 0
            if self.playerb.life <= 0:
                score -= 1000
            if self.playera.life <= 0:
                score += 1000

            score += self.playerb.stamina - self.playera.stamina
            score += (self.playerb.rect.centerx - self.playera.rect.centerx) / 10
            return score  
    
        
        def alpha_beta(self, depth, alpha, beta, maximizing_player):
            if depth == 0 or self.is_terminal_state():
                return self.evaluate_state()

            if maximizing_player:
                max_eval = float('-inf')
                for move in self.get_possible_moves(maximizing_player):
                    self.make_move(move, maximizing_player)
                    eval = self.alpha_beta(depth - 1, alpha, beta, False)
                    self.undo_move(move, maximizing_player)
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
                return max_eval
            else:
                min_eval = float('inf')
                for move in self.get_possible_moves(maximizing_player):
                    self.make_move(move, maximizing_player)
                    eval = self.alpha_beta(depth - 1, alpha, beta, True)
                    self.undo_move(move, maximizing_player)
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
                return min_eval    
            
        def get_best_move(self, depth=3):
                best_move = None
                best_value = float('-inf')
                alpha = float('-inf')
                beta = float('inf')

                for move in self.get_possible_moves(maximizing_player=True):
                    self.make_move(move, maximizing_player=True)
                    move_value = self.alpha_beta(depth - 1, alpha, beta, False)
                    self.undo_move(move, maximizing_player=True)

                    if move_value > best_value:
                        best_value = move_value
                        best_move = move

                return best_move
    
        def make_move(self, move, maximizing_player):
            if maximizing_player:
                for action in move:
                    self.apply_action(action, self.playerb)
            else:
                for action in move:
                    self.apply_action(action, self.playera)

        def undo_move(self, move, maximizing_player):
            if maximizing_player:
                for action in reversed(move):
                    self.revert_action(action, self.playerb)
            else:
                for action in reversed(move):
                    self.revert_action(action, self.playera)   
        
        def apply_action(self, action, player):
            if action == 'left':
                player.rect.x -= player.speed
                player.X_change = -player.speed
            elif action == 'right':
                player.rect.x += player.speed
                player.X_change = player.speed
            elif action == 'jump':
                player.deploy_jump()
            elif action == 'down':
                player.deploy_fall()
            elif action == 'sword':
                player.deploy_strike()
            elif action == 'shield':
                player.deploy_shield()
            elif action == 'jump_left_downstrike':
                player.rect.x -= player.speed
                player.X_change = -player.speed
                player.deploy_jump()
                player.deploy_strike()
            elif action == 'jump_right_downstrike':
                player.rect.x += player.speed
                player.X_change = player.speed
                player.deploy_jump()
                player.deploy_strike()

        def revert_action(self, action, player):
            if action == 'left':
                player.rect.x += player.speed
                player.X_change = 0
            elif action == 'right':
                player.rect.x -= player.speed
                player.X_change = 0
            elif action == 'jump':
                player.Y_change = 0  # Reverting jump might be tricky, adjust as necessary
            elif action == 'down':
                player.Y_change = 0  # Reverting fall might be tricky, adjust as necessary
            elif action == 'sword':
                player.striking = False
                player.sword_hurtbox = False
                player.stamina += 1
            elif action == 'shield':
                player.shielding = False
                player.shield_block = False
                player.stamina += 1
            elif action == 'jump_left_downstrike':
                player.rect.x += player.speed
                player.X_change = 0
                player.revert_jump()
                player.revert_strike()
            elif action == 'jump_right_downstrike':
                player.rect.x -= player.speed
                player.X_change = 0
                player.revert_jump()
                player.revert_strike()
                
                
        def is_terminal_state(self):
            return self.playera.life <= 0 or self.playerb.life <= 0   
        
        
        
        def get_possible_moves(self, maximizing_player):
            if maximizing_player:
                sequence = [None]
                if not self._has_stamina():
                    sequence = self._avoid()
                elif self._is_on_top():
                    possible_sequences = [self.down_strike, self.walk_right, self.walk_left, self.jump_left_downstrike, self.jump_right_downstrike] 
                    sequence = random.choice(possible_sequences)
                elif self._is_under():
                    if self._has_stamina(3):
                        possible_sequences = [self.dash_left, self.dash_right, self.walk_left * 10, self.walk_right * 10, self.jump_left_downstrike, self.jump_right_downstrike]
                        sequence = random.choice(possible_sequences)
                    else:
                        possible_sequences = [self.walk_left * 2, self.walk_right * 2, self.jump_left_downstrike, self.jump_right_downstrike]
                        sequence = random.choice(possible_sequences)
                elif self._is_far():
                    if self._is_left():
                        sequence = self.walk_left
                    else:
                        sequence = self.walk_right
                elif self._is_close():
                    if self.playera.striking:
                        sequence = self.shield
                    else:
                        if self._is_left():
                            sequence = [[self.input_dict['left'], self.input_dict['sword']]]
                        else:
                            sequence = [[self.input_dict['right'], self.input_dict['sword']]]
                    if self.playerb.striking:
                        if self._is_left():
                            sequence = self.walk_left
                        if self._is_right():
                            sequence = self.walk_right
                elif self._is_left() & self._is_medium():
                    if self._has_stamina(2):
                        possible_sequences = [self.jump_left_downstrike, self.dash_left, self.walk_left]
                        sequence = random.choice(possible_sequences)
                    else:
                        possible_sequences = [self.jump_left_downstrike, self.walk_left]
                        sequence = random.choice(possible_sequences)
                elif self._is_right() & self._is_medium():
                    if self._has_stamina(2):
                        possible_sequences = [self.jump_right_downstrike, self.dash_right, self.walk_right]
                        sequence = random.choice(possible_sequences)
                    else:
                        possible_sequences = [self.jump_right_downstrike, self.walk_right]
                        sequence = random.choice(possible_sequences)
                elif self._is_left() & (self.playera.land_downstrike_stun is True):
                    if self._is_far() & self._has_stamina(3):
                        possible_sequences = [self.walk_left, self.dash_left]
                        sequence = random.choice(possible_sequences)
                    if (self._is_medium() or self._is_close()) & self._has_stamina(1):
                        sequence = self.walk_left + self.sword
                elif self._is_right() & (self.playera.land_downstrike_stun is True):
                    if self._is_far() & self._has_stamina(3):
                        possible_sequences = [self.walk_right, self.dash_right]
                        sequence = random.choice(possible_sequences)
                    if (self._is_medium() or self._is_close()) & self._has_stamina(1):
                        sequence = self.walk_right + self.sword

                return [sequence]
            else:
                return [
                    self.walk_left,
                    self.walk_right,
                    self.dash_left,
                    self.dash_right,
                    self.jump_left_downstrike,
                    self.jump_right_downstrike,
                    self.down_strike
                ]

    
    
        def _alpha_beta_input(self):
            
            self._check_sequence_break()
            
            
            best_move = self.get_best_move()
            ai_key_dict_copy = self.ai_key_dict.copy()
            jump_found = False  # Flag to track if jumping actions are found in best move

            if best_move is not None:
                for move in best_move:
                    if isinstance(move, list):  # Handle multi-action sequences
                        for action in move:
                            ai_key_dict_copy[action] = 1
                            if not jump_found and action in ['jump_left_downstrike', 'jump_right_downstrike', 'jump']:
                                ai_key_dict_copy[self.input_dict['jump']] = 1
                                jump_found = True  # Set flag to avoid redundant checks
                    else:
                        ai_key_dict_copy[move] = 1
                        if not jump_found and move in ['jump_left_downstrike', 'jump_right_downstrike', 'jump']:
                            ai_key_dict_copy[self.input_dict['jump']] = 1
                            jump_found = True  # Set flag to avoid redundant checks

                    if jump_found:
                        break  # Exit loop if jumping action is found

            return ai_key_dict_copy
    
        def evaluate_fitness(self, chromosome):
            self.make_move_GA(chromosome, maximizing_player=True)
            fitness = self.evaluate_state()
            self.undo_move_GA(chromosome, maximizing_player=True)
            return fitness
        
        
        def select_parents(self, population, fitnesses):
            total_fitness = sum(fitnesses)
            selection_probs = [fitness / total_fitness for fitness in fitnesses]
            parents = random.choices(population, weights=selection_probs, k=2)
            return parents
        
        
        def crossover(self, parent1, parent2):
            crossover_point = random.randint(1, max(len(parent1) - 1, 1))
            child1 = parent1[:crossover_point] + parent2[crossover_point:]
            child2 = parent2[:crossover_point] + parent1[crossover_point:]
            return child1, child2
        
        
        def mutate(self, chromosome):
            for i in range(len(chromosome)):
                if random.random() < 0.01:  # Mutation rate of 1%
                     chromosome[i] = random.choice(self.actions)
            return chromosome
         
       
        def get_possible_sequences(self, maximizing_player=True):
            return [self._choose_heuristic() for _ in range(random.randint(0, 20))]
        
        
        def make_move_GA(self, move, maximizing_player):
        
            
            if isinstance(move, list):
                for action in move:
                    self.apply_action(action, self.playerb if maximizing_player else self.playera)
            else:
                raise TypeError(f"Expected move to be a list, got {type(move)} instead.")

        def undo_move_GA(self, move, maximizing_player):
            if isinstance(move, list):
                for action in reversed(move):
                    self.revert_action(action, self.playerb if maximizing_player else self.playera)
            else:
                raise TypeError(f"Expected move to be a list, got {type(move)} instead.")
            

        def genetic_algorithm(self, population_size=20, generations=10):
            population = [self.get_possible_sequences() for _ in range(population_size)]

            for generation in range(generations):
                fitnesses = [self.evaluate_fitness(chromosome) for chromosome in population]
                new_population = []

                for _ in range(population_size // 2):
                    parent1, parent2 = self.select_parents(population, fitnesses)
                    child1, child2 = self.crossover(parent1, parent2)
                    new_population.append(self.mutate(child1))
                    new_population.append(self.mutate(child2))

                population = new_population

                best_fitness = max(fitnesses)
                if best_fitness >= 1000:
                    break

            best_chromosome = population[fitnesses.index(max(fitnesses))]
            return best_chromosome
        
        
        def get_best_sequence(self):
            best_move_sequence = self.genetic_algorithm()
            return best_move_sequence
        
        
        def _genetic_algorithm_input(self):
            best_move = self.get_best_sequence()
            ai_key_dict_copy = self.ai_key_dict.copy()

            if best_move is not None:
                for move in best_move:
                    # Flatten any nested lists in the move sequence
                    if isinstance(move, list):
                        for action in move:
                            if isinstance(action, list):
                                # Handle nested lists if present
                                ai_key_dict_copy[tuple(action)] = 1  # Convert list to tuple for hashability
                            else:
                                ai_key_dict_copy[action] = 1
                    else:
                        ai_key_dict_copy[move] = 1

            return ai_key_dict_copy




        
        def _hard_heuristics(self):
            pass

    def scale(self, val):
        
        # divide by 60 is so I can pass same values as before scaling was implemented
        if isinstance(val,(int,float)):
            return math.floor((val/60)*self.scale_factor)
        if isinstance(val,(list,tuple)):
            return [math.floor((i/60)*self.scale_factor) for i in val]

    def _setup_screen(self):
        '''Creates pygame screen and draws background.'''

        monitor_size = (pygame.display.Info().current_w,pygame.display.Info().current_h)
        # monitor_size = (1000,700)
        
        horiz = monitor_size[0]/self.screen_ratio[0]
        vert = monitor_size[1]/self.screen_ratio[1]
        self.scale_factor = min(horiz,vert)
        self.screen_size = (math.floor(self.scale_factor*self.screen_ratio[0]),math.floor(self.scale_factor*self.screen_ratio[1]))

        self.screen = pygame.display.set_mode(self.screen_size)
        
        # title and icon
        pygame.display.set_caption('Battle')
    

        self.player_1_heart_sprite = pygame.image.load('res/images/heart_player_1.png').convert_alpha()
        self.player_1_heart_sprite = pygame.transform.scale(self.player_1_heart_sprite, self.scale((30,30)))
        self.player_2_heart_sprite = pygame.image.load('res/images/heart_player_2.png').convert_alpha()
        self.player_2_heart_sprite = pygame.transform.scale(self.player_2_heart_sprite, self.scale((30,30)))        
        self.stamina_sprite = pygame.image.load('res/images/stamina.png').convert_alpha()
        self.stamina_sprite = pygame.transform.scale(self.stamina_sprite, self.scale((20,20)))

    def _setup_menu(self):

        self.menu_dict = {'main': True, 'start_fight': False}
        self.pointer = 0

    def _setup_audio(self):

        self.sword_hit_sound = pygame.mixer.Sound('res/sounds/sword_hit.mp3')
        self.sword_hit_shield_sound = pygame.mixer.Sound('res/sounds/sword_hit_shield.wav')
        self.sword_hit_shield_sound.set_volume(.3)
    
    def play_startup_sound(self):
        self.start_game_sound.play(loops=-1)
        
    def update_display(self):
        pygame.display.update()
        self.fps_clock.tick(self.fps)

    def show_background(self):
        '''Draws background.'''
        # self.background = pygame.image.load('res/images/background.png').convert_alpha()
        # self.background = pygame.transform.scale(self.background, self.screen_size)

        #fill white color
        self.screen.fill((255,255,255))

        # self.screen.fill((0,0,0))
        # self.screen.blit(self.background,(0,0))
        pygame.draw.rect(self.screen,(0,0,0),(0,self.screen_size[1]*.78, self.screen_size[0],self.scale(10)))

    def _setup_elements(self):
        '''Creates character and environment elements.'''

        self.player1 = self.Player(self.screen, self.scale, facing_left = False)
        self.player2 = self.Player(self.screen, self.scale, facing_left = True)
        self._setup_ai()

    def _setup_ai(self):
        if self.ai is True:
            self.ai_enemy = self.AIEnemy(self.player2.input_dict, self.player1, self.player2)
            self.ai_enemy.set_level(self.ai_difficulty)

    def _setup_fonts(self):
        '''Creates fonts for various texts.'''

        self.score_font = pygame.font.Font('freesansbold.ttf', self.scale(32))
        #set font color

        self.over_font = pygame.font.Font('freesansbold.ttf', self.scale(48))

    def handle_menu(self):

        if (self.main_menu is True):
            
            if self.menu_dict['main'] == True:
                self._show_main_menu()
            elif self.menu_dict['start_fight'] == True:
                self._show_start_fight_menu()
            elif self.menu_dict['difficulty'] == True:
                self._show_difficulty_menu()


    def _show_main_menu(self):
          keys = pygame.event.get(pygame.KEYDOWN)
          if keys:
              if keys[0].key in (self.player1.input_dict['down'], self.player2.input_dict['down']):
                  if self.pointer == 0:
                      self.pointer += 1
              if keys[0].key in (self.player1.input_dict['jump'], self.player2.input_dict['jump']):
                  if self.pointer == 1:
                      self.pointer -= 1
              if keys[0].key in (pygame.K_SPACE, self.player1.input_dict['sword'], self.player2.input_dict['sword']):
                  if self.pointer == 0:
                      self.menu_dict['main'] = False
                      self.menu_dict['difficulty'] = True
                  else:
                      self.ai = False
                      self.menu_dict['main'] = False
                      self.menu_dict['start_fight'] = True
              if keys[0].key == pygame.K_ESCAPE:
                  self.running = False

          self._show_text('TELIGATI RUMBLE', font=self.over_font)
          texts = ['VS CPU', 'VS PLAYER']
          self._show_text(texts, text_y=250, pointer=self.pointer)
          
    def _show_difficulty_menu(self):
          keys = pygame.event.get(pygame.KEYDOWN)
          if keys:
              if keys[0].key in (self.player1.input_dict['down'], self.player2.input_dict['down']):
                  if self.pointer < 2:
                      self.pointer += 1
              if keys[0].key in (self.player1.input_dict['jump'], self.player2.input_dict['jump']):
                  if self.pointer > 0:
                      self.pointer -= 1
              if keys[0].key in (pygame.K_SPACE, self.player1.input_dict['sword'], self.player2.input_dict['sword']):
                  if self.pointer == 0:
                      self.ai = True
                      self.ai_difficulty = 'easy'
                  elif self.pointer == 1:
                      self.ai = True
                      self.ai_difficulty = 'medium'
                  elif self.pointer == 2:
                      self.ai = True
                      self.ai_difficulty = 'hard'

                  self._setup_ai()
                  self.menu_dict['difficulty'] = False
                  self.menu_dict['start_fight'] = True
              if keys[0].key == pygame.K_ESCAPE:
                  self.menu_dict['difficulty'] = False 
                  self.menu_dict['main'] = True

          self._show_text('SELECT DIFFICULTY', font=self.over_font)
          texts = ['EASY (RETARDED)', 'MEDIUM (SANE)', 'HARD (REAL SHIT)']
          self._show_text(texts, text_y=250, pointer=self.pointer) 

    def _show_start_fight_menu(self):

            self._show_text('Press SPACE to start fight', 150)
            
            keys = (pygame.event.get(pygame.KEYDOWN))
            if len(keys) > 0:
                
                if keys[0].key == pygame.K_BACKSPACE:
                    self.menu_dict['main'] = True
                    self.menu_dict['start_fight'] = False
                
                if keys[0].key == pygame.K_SPACE:
                    self.menu = False
                
                if keys[0].key == pygame.K_ESCAPE:
                    self.running = False

    def _show_text(self, text, text_y = 150, pointer = None, font = None):

        if not isinstance(text, list):
            text = [text]
        if font is None:
            font = self.score_font

        center_width = self.screen_size[0]/2
        text_y = self.scale(text_y)

        for i,t in enumerate(text):
            render_text = font.render(t, True, (0,0,0))
            render_text_rect = render_text.get_rect(midtop=(center_width,text_y))
            self.screen.blit(render_text, render_text_rect)
            if (pointer is not None) & (i == pointer):
                
                self.player1.sword_rect.midright = (render_text_rect.left-self.scale(2),render_text_rect.centery-self.scale(4))
                self.screen.blit(self.player1.sword_sprite,self.player1.sword_rect)
            
            text_y = render_text_rect.bottom + self.scale(1)
            
    def show_data(self):

        self._show_lives()
        self._show_stamina()

    def _show_lives(self):

        self.screen.blit(self.player_1_heart_sprite, self.scale((15, 23)))
        self.screen.blit(self.player_2_heart_sprite, self.scale((925,23)))
        self.player_1_health_color = (26,208,121)
        # self.player_1_health_color = (15,111,65)

        self.player_2_health_color = (243,75,64)
        # self.player_2_health_color = (102,13,13)

        y = self.scale(23)
        size = self.scale(30)

        for i in range(self.player1.life):
            x = self.scale(60) + self.scale(30)*i
            pygame.draw.rect(self.screen,self.player_1_health_color,[x, y, size, size])
        for i in range(self.player2.life):
            x = self.screen_size[0]-self.scale(80)-self.scale(30)*i
            pygame.draw.rect(self.screen,self.player_2_health_color,[x, y, size, size])

    def _show_stamina(self):

        y = self.scale(70)
        size = self.scale(20)

        for i in range(self.player1.stamina):
            x = self.scale(60) + self.scale(30)*i
            pygame.draw.rect(self.screen,(0,0,0),[x, y, size, size],0,2)
        for i in range(self.player2.stamina):
            x = self.screen_size[0]-self.scale(75)-self.scale(30)*i
            pygame.draw.rect(self.screen,(0,0,0),[x, y, size, size],0,2)
        
        self.screen.blit(self.stamina_sprite, self.scale((20, 70)))
        self.screen.blit(self.stamina_sprite, self.scale((925, 70)))

    def handle_events(self):
        '''Quits game if exit is pressed.'''

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
        
            if event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode((event.w, event.h),
                                                    pygame.RESIZABLE)
                self.player1.ground = round(self.screen.get_height()*0.78)
                self.player2.ground = round(self.screen.get_height()*0.78)
                over_font_size = round(min(self.screen.get_width()*.08,self.screen.get_height()*.08))
                self.over_font = pygame.font.Font('freesansbold.ttf', over_font_size)

    def handle_gameover(self):

        self._check_game_over()
        self._handle_reset()

    def _check_game_over(self):

        texts = ['Press SPACE to restart', 'Press BACK to return to main menu']
        
        if (self.player1.life <= 0) & (self.player2.life >= 1):

            self._show_text('Player 2 wins', font = self.over_font)
            self._show_text(texts, 225)
            self.player1.rect.y = -2000
            self.player1.knockback = True
            self.game_over = True

        elif (self.player2.life <= 0) & (self.player1.life >= 1):

            self._show_text('Player 1 wins', font = self.over_font)
            self._show_text(texts, 225)
            self.player2.rect.y = -2000
            self.player2.knockback = True
            self.game_over = True 
        
        elif (self.player2.life <= 0) & (self.player1.life <= 0):
            self._show_text('Draw', font = self.over_font)
            self._show_text(texts, 225)
            self.player1.rect.y, self.player2.rect.y = -2000,-2000
            self.player1.knockback, self.player2.knockback = True, True
            self.game_over = True  
    
    def _handle_reset(self):

        if self.game_over is True:

            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                self.game_over = False
                max_stamina1 = self.player1.max_stamina
                max_stamina2 = self.player2.max_stamina

                self._setup_elements()
                self.player1.max_stamina,self.player1.stamina,self.player1.life = max_stamina1,max_stamina1,10-max_stamina1
                self.player2.max_stamina,self.player2.stamina,self.player2.life = max_stamina2,max_stamina2,10-max_stamina2
            
            if keys[pygame.K_BACKSPACE]:
                self.game_over = False
                self.menu = True
                self.menu_dict['main'] = True
                self.menu_dict['start_fight'] = False
                self._setup_elements()

    def handle_input(self):

        keys = pygame.key.get_pressed()
        self._player_movement(self.player1, keys)
        
        if self.ai is True:
            ai_input = self.ai_enemy.get_input()
            if ai_input is not None:
                keys = ai_input
                
        
        
        self._player_movement(self.player2, keys)

    def _player_movement(self, player, keys):
        
       
        if player.is_ready():
            # left movement
            if keys[player.input_dict['left']]:
            
                if player.facing_left is False:
                    player.facing_left = True
                    player.flip_player()

                player.X_change = -player.speed
                player.check_dash('Left')
            
            # right movement
            if keys[player.input_dict['right']]:

                if player.facing_left is True:
                    player.facing_left = False
                    player.flip_player()

                player.X_change = player.speed
                player.check_dash('Right')
                        
            # jumping
            if keys[player.input_dict['jump']]:
                player.deploy_jump()
            
            # downstrike
            if keys[player.input_dict['down']]:
                player.deploy_downstrike()

            # sword
            if (keys[player.input_dict['sword']]):
                player.deploy_strike()
            
            # shield
            if keys[player.input_dict['shield']]:
                player.deploy_shield()

            # stopping
            if keys[player.input_dict['right']] and keys[player.input_dict['left']]: 
                player.X_change = 0
            if not keys[player.input_dict['right']] and not keys[player.input_dict['left']]:
                player.X_change = 0
                player.check_dash()

    def handle_collisions(self):
        '''Handles collisions from both players and swords.'''
        
        self._handle_sword_collisions()
        self._handle_player_collisions()
        self._handle_downstrike_collisions()

    def _handle_player_collisions(self):
        '''Handles player collisions.'''
        
        # check collision between 2 players
        collide = bool(self.player1.rect.colliderect(self.player2.rect))

        if collide is True:
            self._calc_player_collision(self.player1, self.player2)
            self._calc_player_collision(self.player2, self.player1)
        else:
            self.player1.on_top = False
            self.player2.on_top = False
            
    def _calc_player_collision(self,playera,playerb):
        
        playera.on_top = self._edge_detection(playera.rect.bottom, playerb.rect.top)

        if (playera.on_top is False) & (playerb.on_top is False):
            if playera.rect.x < playerb.rect.x:
                if playera.X_change > 0:
                    playera.X_change = 0
                if playerb.X_change < 0:
                    playerb.X_change = 0
        
        # if player a is above player b
        if playera.rect.y < playerb.rect.y:
            # player a can't fall, player b can't jump
            if playera.Y_change > 0:
                playera.Y_change = 0
            if playerb.Y_change < 0:
                playerb.Y_change = 0
        
        if playera.on_top is True:
            playera.rect.bottom = playerb.rect.top+1
            self._edge_detection(playera.rect.bottom, playerb.rect.top)
    
    def _edge_detection(self,edgea,edgeb,margin=30):

        return abs(edgea - edgeb) < self.scale(margin)

    def _handle_sword_collisions(self):

        self._calc_sword_collisions(self.player1, self.player2)
        self._calc_sword_collisions(self.player2, self.player1)

    def _calc_sword_collisions(self, playera, playerb):
        
        # if sword is deployed
        if playera.sword_hurtbox is True:
            
            # check collisions
            playerb_collide = bool(playera.sword_rect.colliderect(playerb.rect))
            
            if playerb.shielding is True:
                shieldb_collide = bool(playera.sword_rect.colliderect(playerb.shield_rect))
            else:
                shieldb_collide = False
            
            # calc left/right for knockback
            if playera.rect.centerx < playerb.rect.centerx:
                playerb.knockback_speed = abs(playerb.knockback_speed)
                playera.knockback_speed = -abs(playerb.knockback_speed)
            else:
                playerb.knockback_speed = -abs(playerb.knockback_speed)
                playera.knockback_speed = abs(playerb.knockback_speed)
            
            # hit shield and not player``
            if shieldb_collide and not playerb_collide:
                self.do_shield_hit(playera)

            # hit player
            if playerb_collide:
                
                if playera.rect.centerx < playerb.rect.centerx:
                    if (playerb.facing_left) and (playerb.shield_block):
                        self.do_shield_hit(playera)
                    else:
                        self.do_hit(playerb)

                if playera.rect.centerx > playerb.rect.centerx:
                    if (not playerb.facing_left) and (playerb.shield_block):
                        self.do_shield_hit(playera)
                    else:
                        self.do_hit(playerb)
    
    def _handle_downstrike_collisions(self):

        self._calc_downstrike_collisions(self.player1, self.player2)
        self._calc_downstrike_collisions(self.player2, self.player1)

    def _calc_downstrike_collisions(self, playera, playerb):
        
        # if sword is deployed
        if playera.downstriking is True:
            
            # check collisions
            playerb_collide = bool(playera.downstrike_rect.colliderect(playerb.rect))

            # hit player
            if playerb_collide:
                self.do_hit(playerb,knockback=False)

    def do_hit(self, player, knockback=True):
        if player.invinsible is False: 
            player.take_hit(knockback)
            self.sword_hit_sound.play()
    
    def do_shield_hit(self,player):
        if player.knockback is False:
            player.stamina = 0
            self.sword_hit_shield_sound.play()
            player.deploy_knockback()

if __name__ == "__main__":
    
    game = Game()

    while game.running is True:

        game.show_background()

        if game.menu is True:
            game.handle_menu()

        else:
            
            game.handle_gameover()
            game.handle_input()

            game.player1.update()
            game.player2.update()

            game.handle_collisions()

            game.player1.movement()
            game.player2.movement()

        game.player1.show()
        game.player2.show()
        
        game.show_data()
        game.handle_events()  
        game.update_display()