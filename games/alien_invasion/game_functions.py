#######################################################
# Program   : game_functions.py
# Author    : Aaron Rioflorido
#
# Function  : Stores the game functions for the Alien Invasion game.
#
#######################################################
import sys, pygame, json
from bullet import Bullet
from alien import Alien
from star import Star
from random import randint
from time import sleep


def fire_bullet(ai_settings, screen, ship, bullets):
    """Fire a bullet if limit not reached yet."""
    if len(bullets) < ai_settings.bullets_allowed:
        # Create a new bullet and add it to the bullets group.
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)


def start_game(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """Start/Reset the game."""
    # Hide the mouse cursor.
    pygame.mouse.set_visible(False)

    # Reset the game statistics and game settings.
    ai_settings.initialize_dynamic_settings()
    stats.reset_stats()
    stats.game_active = True

    # Reset the scoreboard images.
    sb.prep_images()

    empty_aliens_and_bullets_lists(aliens, bullets)
    create_fleet(ai_settings, screen, ship, aliens)

    # Center the Ship
    ship.center_ship()


def load_high_score(ai_settings, stats):
    """Load saved high score."""
    try:
        with open(ai_settings.hs_save_file) as fileObj:
            stats.high_score = json.load(fileObj)
    except PermissionError as exception_msg:
        abort_program("Unable to load '{}'.".format(ai_settings.hs_save_file), exception_msg)
    except IsADirectoryError as exception_msg:
        abort_program("'{}' is a directory instead of a file.".format(ai_settings.hs_save_file), exception_msg)
    except FileNotFoundError:
        stats.high_score = 0


def save_high_score(ai_settings, stats):
    """Save the high score to a file."""
    try:
        with open(ai_settings.hs_save_file, 'w') as fileObj:
            json.dump(stats.high_score, fileObj)
    except PermissionError as exception_msg:
        abort_program("Unable to save '{}'.".format(ai_settings.hs_save_file), exception_msg)
    except IsADirectoryError as exception_msg:
        abort_program("'{}' is a directory instead of a file.".format(ai_settings.hs_save_file), exception_msg)


def check_keydown_events(event, ai_settings, screen, stats, sb, ship, aliens, bullets):
    """Respond to keypresses."""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_UP:
        ship.moving_forward = True
    elif event.key == pygame.K_DOWN:
        ship.moving_backward = True
    elif event.key == pygame.K_LSHIFT:
        ship.turbo_mode = True
    elif event.key == pygame.K_SPACE:
        fire_bullet(ai_settings, screen, ship, bullets)
    elif event.key == pygame.K_p and not stats.game_active:
        # Start the game when 'P' is pressed.
        start_game(ai_settings, screen, stats, sb, ship, aliens, bullets)
    elif event.key == pygame.K_q:
        sys.exit()


def check_keyup_events(event, ship):
    """Respond to key releases."""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False
    elif event.key == pygame.K_UP:
        ship.moving_forward = False
    elif event.key == pygame.K_DOWN:
        ship.moving_backward = False
    elif event.key == pygame.K_LSHIFT:
        ship.turbo_mode = False


def check_play_button(ai_settings, screen, stats, sb, ship, aliens, bullets, play_button, mouse_x, mouse_y):
    """Start a new game when the player clicks the Play button."""
    play_button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)

    if play_button_clicked and not stats.game_active:
        start_game(ai_settings, screen, stats, sb, ship, aliens, bullets)


def check_events(ai_settings, screen, stats, sb, ship, aliens, bullets, play_button):
    """Respond to keypresses and mouse events."""
    # Event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, screen, stats, sb, ship, aliens, bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos() # Mouse cursor x and y coordinates
            check_play_button(ai_settings, screen, stats, sb, ship, aliens, bullets, play_button, mouse_x, mouse_y)


def get_number_alien_x(ai_settings, alien_width):
    """Determine the number of aliens that fit in a row."""
    available_space_x = ai_settings.screen_width - 2 * alien_width
    return int(available_space_x / (2 * alien_width))


def get_number_rows(ai_settings, ship_height, alien_height):
    """Determine the number of rows of aliens that fit on the screen."""
    available_space_y = ai_settings.screen_height - (3 * alien_height) - ship_height
    return int(available_space_y / (2 * alien_height))


def create_alien(ai_settings, screen, aliens, alien_number, row_number):
    """Create an alien and place it in the row"""
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
    alien.rect.x = alien.x
    aliens.add(alien)


def create_fleet(ai_settings, screen, ship, aliens):
    """Create a full fleet of aliens."""
    # Create an alien and find the number of aliens in a row.
    alien = Alien(ai_settings, screen)
    number_aliens_x = get_number_alien_x(ai_settings, alien.rect.width)
    number_rows = get_number_rows(ai_settings, ship.rect.height, alien.rect.height)

    # Create the fleet of aliens.
    [create_alien(ai_settings, screen, aliens, alien_number, row_number) for row_number in range(number_rows) for alien_number in range(number_aliens_x)]


def change_fleet_direction(ai_settings, aliens):
    """Drop the entire fleet and change the fleet's direction."""
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1


def check_fleet_edges(ai_settings, aliens):
    """Respond appropriately if any aliens have reached an edge."""
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break


def ship_hit(ai_settings, stats, screen, sb, ship, aliens, bullets):
    """Respond to ship being hit by alien."""
    if stats.ships_left > 0:
        # Decrement ships_left
        stats.ships_left -= 1

        # Update scoreboard.
        sb.prep_ships()

        empty_aliens_and_bullets_lists(aliens, bullets)

        # Create a new fleet and center the ship.
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()

        # Pause the game for a moment.
        sleep(0.5)
    else:
        stats.game_active = False

        # Show the mouse cursor
        pygame.mouse.set_visible(True)


def check_aliens_bottom(ai_settings, stats, screen, sb, ship, aliens, bullets):
    """Check if any aliens have reached the bottom of the screen."""
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            # Mission failed.
            ship_hit(ai_settings, stats, screen, sb, ship, aliens, bullets)
            break


def update_aliens(ai_settings, stats, screen, sb, ship, aliens, bullets):
    """Check if the fleet is at an edge, and then update the positions of all aliens in the fleet."""
    check_fleet_edges(ai_settings, aliens)
    aliens.update()

    # Lok for alien-ship collisions.
    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(ai_settings, stats, screen, sb, ship, aliens, bullets)

    # Look for aliens hitting the bottom of the screen
    check_aliens_bottom(ai_settings, stats, screen, sb, ship, aliens, bullets)


def check_high_score(ai_settings, stats, sb):
    """Check to see of there's a new high score."""
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()
        save_high_score(ai_settings, stats)


def check_bullet_alien_collisions(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """Respond to bullet-alien collisions."""
    # Remove any bullets and aliens that have collided.
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)

    if collisions:
        for aliens in collisions.values():
            stats.score += ai_settings.alien_points * len(aliens)
            sb.prep_score()
        check_high_score(ai_settings, stats, sb)

    if len(aliens) == 0:
        # If the entire fleet is destroyed, start a new level.
        bullets.empty()
        ai_settings.increase_speed()

        # Increase level.
        stats.level += 1
        sb.prep_level()

        create_fleet(ai_settings, screen, ship, aliens)


def empty_aliens_and_bullets_lists(aliens, bullets):
    """Empty the list of aliens and bullets"""
    aliens.empty()
    bullets.empty()


def update_bullets(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """Update position of bullets and get rid of old bullets."""
    # Update bullet positions
    bullets.update()

    # Get rid of bullets that have disappeared.
    [bullets.remove(bullet) for bullet in bullets.copy() if bullet.rect.bottom <= 0]

    check_bullet_alien_collisions(ai_settings, screen, stats, sb, ship, aliens, bullets)


def update_screen(ai_settings, screen, stats, sb, ship, aliens, bullets, stars, play_button):
    """Update images on the screen and flip to the new screen."""

    # Redraw the screen during each pass through the loop.
    screen.fill(ai_settings.bg_color)

    # Redraw grid of stars behind all of the objects.
    stars.draw(screen)

    # Draw the score information.
    sb.show_score()

    # Redraw all bullets behind ship and aliens.
    [bullet.draw_bullet() for bullet in bullets.sprites()]
    ship.blitme()
    aliens.draw(screen)

    # Draw the play button if the game is inactive.
    if not stats.game_active:
        play_button.draw_button()

    # Make the most recently drawn screen visible.
    pygame.display.flip()


def create_star(ai_settings, screen, stars):
    """Create a star and place it randomly somewhere in the screen"""
    star = Star(ai_settings, screen)
    star.rect.x = randint(0, screen.get_rect().width)
    star.rect.y = randint(0, screen.get_rect().height)
    stars.add(star)


def create_grid(ai_settings, screen, stars):
    """Create a grid of stars"""
    number_of_stars = randint(20, 50)

    # Create the grid of stars
    [create_star(ai_settings, screen, stars) for _ in range(number_of_stars)]


def abort_program(err_msg, exception_msg=None):
    """Display error message then abort the program."""
    print("Error:", err_msg)
    if exception_msg:
        print("Exception : {}".format(exception_msg))
    sys.exit(1)
