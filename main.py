import pygame
import sys
from pygame.locals import *
from PIL import Image, ImageTk
import time

# Initialize Pygame
pygame.init()

# Adjust constants for a more compact design
WINDOW_WIDTH, WINDOW_HEIGHT = 1024, 600
BACKGROUND_COLOR = (241, 246, 249)
HEADER_COLOR = (255, 255, 255)
TEXT_COLOR = (10, 10, 10)
BUTTON_COLOR = (10, 10, 10)
BUTTON_HOVER_COLOR = (200, 200, 200)
KEYBOARD_COLOR = (30, 30, 30) 
KEY_TEXT_COLOR = (30, 30, 30) 
POPUP_COLOR = (255, 255, 255)
banner = pygame.image.load("banner.png")

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("SOCKIO - San Sebastian College Recoletos De Cavite")

# Adjust fonts for compact UI
font = pygame.font.Font("poppins-light.ttf", 12)
header_font = pygame.font.SysFont("Arial", 16)
search_font = pygame.font.SysFont("Arial", 14)

class SockioApp:
    def __init__(self):
        # Initialize categories for product filtering
        self.categories = ["All Meals", "Rice Meals", "Biscuits", "Drinks"]

        self.search_active = False
        self.search_text = ""
        self.products = [
            {"name": "Shanghai Rice Meal", "price": 50, "image": "shanghai.png"},
            {"name": "Spaghetti", "price": 30, "image": "spaghetti.png"},
            {"name": "Sinigang Rice Meal", "price": 55, "image": "sinigang.png"},
            {"name": "Fried Chicken Rice Meal", "price": 65, "image": "chicken.png"},
            {"name": "C2 Drink", "price": 25, "image": "c2.png"},
            {"name": "Water Bottle", "price": 15, "image": "water.png"},
        ]
        self.filtered_products = self.products.copy()
        self.cart_items = []
        self.selected_product = None
        self.selected_quantity = 1
        self.virtual_keyboard = self.create_virtual_keyboard()
        self.keyboard_triggered = False  # Initialize the keyboard trigger state
        self.mouse_pressed = False

        # Scroll variables
        self.scroll_offset = 0  # Start position of the scroll
        self.scroll_bar_height = 0  # Height of the scroll bar handle
        self.mouse_drag_start_y = None  # Track the initial mouse Y position when dragging
        self.scroll_bar_rect = pygame.Rect(WINDOW_WIDTH - 15, 80, 15, WINDOW_HEIGHT - 80)  # Position and size of scroll barself.scroll_bar_rect = pygame.Rect(WINDOW_WIDTH - 15, 80, 15, WINDOW_HEIGHT - 80)  # Position and size of scroll bar

    def load_image(self, image_path, size=(100, 100)):
        try:
            img = Image.open(image_path)
            img = img.resize(size)  # Resize the image
            mode = img.mode
            size = img.size
            data = img.tobytes()
            return pygame.image.fromstring(data, size, mode)  # Convert to Pygame surface
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return pygame.Surface(size)  # Return a placeholder surface if loading fails

    def draw_scroll_bar(self):
        total_height = len(self.filtered_products) * 220  # Total content height
        visible_area = WINDOW_HEIGHT - 80  # Visible window area for products

        # Calculate the size of the scroll handle
        if total_height > visible_area:
            self.scroll_bar_height = max(visible_area * visible_area / total_height, 40)
            handle_y = 80 + (self.scroll_offset * visible_area / total_height)
        else:
            self.scroll_bar_height = visible_area  # Full height if no scrolling
            handle_y = 80

        # Draw the scroll bar background
        pygame.draw.rect(screen, (200, 200, 200), self.scroll_bar_rect)

        # Draw the scroll handle (the draggable part of the scroll bar)
        scroll_handle_rect = pygame.Rect(
            self.scroll_bar_rect.x, handle_y, self.scroll_bar_rect.width, self.scroll_bar_height
        )
        pygame.draw.rect(screen, (100, 100, 100), scroll_handle_rect)


    def handle_scroll(self):
        """Handle scroll bar interaction with mouse events."""
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        # Check if the scrollbar handle is clicked and dragged
        if mouse_pressed and self.scroll_bar_rect.collidepoint(mouse_pos):
            if self.mouse_drag_start_y is None:
                self.mouse_drag_start_y = mouse_pos[1]  # Store initial Y position
            
            # Calculate drag distance
            delta_y = mouse_pos[1] - self.mouse_drag_start_y
            self.mouse_drag_start_y = mouse_pos[1]  # Update start position

            # Calculate proportional scroll offset
            total_height = len(self.filtered_products) * 220  # Total height of product list
            visible_area = WINDOW_HEIGHT - 80  # Height of visible area
            if total_height > visible_area:
                scroll_proportion = visible_area / total_height
                self.scroll_offset += delta_y / scroll_proportion

                # Clamp the scroll offset to valid range
                self.scroll_offset = max(0, min(self.scroll_offset, total_height - visible_area))
        else:
            self.mouse_drag_start_y = None  # Reset drag start position if mouse is released

    def create_virtual_keyboard(self):
        keys = [
            "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P",
            "A", "S", "D", "F", "G", "H", "J", "K", "L", "Z", "X", "C", "V", "B", "N", "M", "Space", "Delete", "Done"
        ]
        key_width, key_height = 60, 40  # Dimensions of each key
        horizontal_spacing, vertical_spacing = 5, 5  # Adjust spacing between keys
        keys_positions = []

        # Calculate keyboard starting position
        keyboard_x = (WINDOW_WIDTH - ((key_width + horizontal_spacing) * 10)) // 2
        keyboard_y = WINDOW_HEIGHT - 190

        # Iterate over the keys to position them
        for i, key in enumerate(keys):
            x = (i % 10) * (key_width + horizontal_spacing) + keyboard_x
            y = (i // 10) * (key_height + vertical_spacing) + keyboard_y
            keys_positions.append((key, (x, y)))

        return keys_positions


    def draw_virtual_keyboard(self):
        if self.keyboard_triggered:
            # Define the keyboard background
            pygame.draw.rect(screen, KEYBOARD_COLOR, (0, WINDOW_HEIGHT - 200, WINDOW_WIDTH, 200))

            # Draw individual keys
            for key, pos in self.virtual_keyboard:
                key_rect = pygame.Rect(pos, (50, 40))  # Adjust key size
                # Change color when hovering over the key
                color = BUTTON_HOVER_COLOR if key_rect.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
                pygame.draw.rect(screen, color, key_rect, border_radius=5)

                # Render the key label
                key_text = font.render(key, True, KEY_TEXT_COLOR)
                screen.blit(key_text, (key_rect.x + 15, key_rect.y + 10))

                # Handle key presses (trigger only on the first click)
                if key_rect.collidepoint(pygame.mouse.get_pos()):
                    if pygame.mouse.get_pressed()[0]:  # Left mouse button pressed
                        if not self.mouse_pressed:  # Trigger only once
                            self.mouse_pressed = True
                            if key == "Done":
                                self.search_active = False
                                self.keyboard_triggered = False

                            elif key == "Delete":
                                self.search_text = self.search_text[:-1]
                                
                            elif key == "Space":
                                self.search_text += " "
                            else:
                                self.search_text += key
                    else:
                        self.mouse_pressed = False


    def white_pannel(self):
        pygame.draw.rect(screen, (230, 230, 230), (180, 50, 829, 80))

    def draw(self):
            screen.fill(BACKGROUND_COLOR)

            

            
            
            self.render_products()
            # Draw the scroll bar
            self.draw_scroll_bar()


            self.white_pannel()
            
            self.create_side_panel()
            self.create_search_bar()
            self.create_header()
            self.render_cart_summary()  # Display cart summary

            if self.search_active:
                self.draw_virtual_keyboard()

            if self.selected_product:
                self.draw_product_popup()
            pygame.display.update()



    def filter_by_search_text(self):
    # Check if the search text is empty
        if not self.search_text.strip():
            self.filtered_products = self.products  # Show all products if no search text
        else:
            # Perform a case-insensitive search
            search_query = self.search_text.lower()
            self.filtered_products = [
                product for product in self.products if search_query in product["name"].lower()
            ]


    def filter_by_category(self):
        if self.selected_category == "All Meals":
            self.filtered_products = self.products  # Show all products
        elif self.selected_category == "Rice Meals":
            self.filtered_products = [
                product for product in self.products if "Rice Meal" in product["name"]
            ]
        elif self.selected_category == "Drinks":
            self.filtered_products = [
                product for product in self.products if "Drink" in product["name"] or "Water" in product["name"]
            ]
        elif self.selected_category == "Biscuits":
            self.filtered_products = [
                product for product in self.products if "Biscuit" in product["name"]
            ]


    def render_cart_summary(self):
        cart_rect = pygame.Rect(0, WINDOW_HEIGHT - 40, WINDOW_WIDTH, 40)
        pygame.draw.rect(screen, (220, 220, 220), cart_rect)

        total_items = len(self.cart_items)
        total_price = sum(item["price"] for item in self.cart_items)

        total_items_text = font.render(f"Total Items: {total_items}", True, TEXT_COLOR)
        total_price_text = font.render(f"Total Price: ₱{total_price}", True, TEXT_COLOR)

        screen.blit(total_items_text, (10, WINDOW_HEIGHT - 30))
        screen.blit(total_price_text, (WINDOW_WIDTH - 200, WINDOW_HEIGHT - 30))



    def create_header(self):

        self.header = self.load_image("banner.png", (WINDOW_WIDTH, 80))

        screen.blit(self.header, (0, 0))


    def create_side_panel(self):
            side_panel_width = 120
            pygame.draw.rect(screen, HEADER_COLOR, (0, 80, side_panel_width, WINDOW_HEIGHT - 80))

            #category_title = font.render("Categories", True, (255, 255, 255))
            #screen.blit(category_title, (10, 100))

            button_y = 120
            for category in self.categories:
                category_button_rect = pygame.Rect(30, button_y, side_panel_width - 60, 60)
                pygame.draw.rect(screen, BUTTON_COLOR, category_button_rect,1, border_radius=5)
                category_button_text = font.render(category, True, TEXT_COLOR)
                screen.blit(category_button_text, (category_button_rect.x -1, category_button_rect.y + 5))

                image = self.load_image(f"{category.lower()}.png", (60, 60 ))
                screen.blit(image, (category_button_rect.x , button_y ))
                if category_button_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                    self.selected_category = category
                    self.filter_by_category()

                button_y += 80

    def create_search_bar(self):
        search_rect = pygame.Rect(WINDOW_WIDTH - 322, 90, 280, 30)
        pygame.draw.rect(screen, (255, 255, 255), search_rect, border_radius=100)
        search_text_surface = search_font.render(self.search_text, True, TEXT_COLOR)
        screen.blit(search_text_surface, (search_rect.x + 10, search_rect.y + 5))

        search_button_rect = pygame.Rect(WINDOW_WIDTH - 120, 90, 80, 30)
        pygame.draw.rect(screen, (255, 255, 255), search_button_rect,1,border_radius=100)
        search_button_text = font.render("Search", True, TEXT_COLOR)
        screen.blit(search_button_text, (search_button_rect.x + 15, search_button_rect.y + 5))

        # Open the keyboard when the search bar is clicked
        if search_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            self.search_active = True
            self.keyboard_triggered = True

        # Trigger search when clicking the search button
        if search_button_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            self.filter_by_search_text()
    def render_products(self):
        start_x = 200  # Start drawing products after the side panel
        start_y = 140 - self.scroll_offset  # Adjust Y position by the scroll offset
        card_width, card_height = 140, 200
        max_cards_per_row = (WINDOW_WIDTH - start_x - 20 - 20) // (card_width + 20)  # Reserve space for the scroll bar

        for i, product in enumerate(self.filtered_products):
            if i % max_cards_per_row == 0 and i > 0:
                start_x = 200
                start_y += card_height + 20

            product_card_rect = pygame.Rect(start_x, start_y, card_width, card_height)
            pygame.draw.rect(screen, (255, 255, 255), product_card_rect, border_radius=5)

            # Load and render the product image at the top of the card (resize to 120x120)
            product_image = self.load_image(product["image"], (120, 120))  # Resize image
            screen.blit(product_image, (start_x + (card_width - 120) // 2, start_y + 10))  # Center the image

            # Render the product name below the image
            product_name_text = font.render(product["name"], True, TEXT_COLOR)
            screen.blit(product_name_text, (start_x + (card_width - product_name_text.get_width()) // 2, start_y + 130))  # Positioned below the image

            # Render the price below the product name
            product_price_text = font.render(f"₱{product['price']}", True, TEXT_COLOR)
            screen.blit(product_price_text, (start_x + (card_width - product_price_text.get_width()) // 2, start_y + 150))  # Positioned below the name

            # Add to Cart button at the bottom
            add_button_rect = pygame.Rect(start_x + 10, start_y + 170, 120, 30)
            pygame.draw.rect(screen, BUTTON_COLOR, add_button_rect,1, border_radius=5)
            add_button_text = font.render("Add to Cart", True, TEXT_COLOR)
            screen.blit(add_button_text, (add_button_rect.x + 25, add_button_rect.y + 5))

            if not self.keyboard_triggered and add_button_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                self.selected_product = product
                self.selected_quantity = 1

            start_x += card_width + 20




    def draw_product_popup(self):
        popup_width, popup_height = 400, 400
        popup_rect = pygame.Rect(
            (WINDOW_WIDTH - popup_width) // 2,  # Center horizontally
            (WINDOW_HEIGHT - popup_height) // 2,  # Center vertically
            popup_width,
            popup_height,
        )
        pygame.draw.rect(screen, POPUP_COLOR, popup_rect, border_radius=10)

        # Load and draw the product image, enlarged (resize to 200x200)
        product_image = self.load_image(self.selected_product["image"], (200, 200))  # Resize image
        screen.blit(product_image, (popup_rect.x + (popup_width - 200) // 2, popup_rect.y + 20))

        # Draw product name and quantity
        product_name_text = font.render(self.selected_product["name"], True, TEXT_COLOR)
        screen.blit(product_name_text, (popup_rect.x + (popup_width - product_name_text.get_width()) // 2, popup_rect.y + 230))

        quantity_text = font.render(f"Quantity: {self.selected_quantity}", True, TEXT_COLOR)
        screen.blit(quantity_text, (popup_rect.x + (popup_width - quantity_text.get_width()) // 2, popup_rect.y + 260))

        # Buttons for adjusting the quantity and completing the action
        button_width, button_height = 40, 40  # Define button sizes
        button_spacing = 20  # Space between the buttons

        plus_button_rect = pygame.Rect(popup_rect.x + (popup_width - button_width * 3 - button_spacing * 2) // 2, popup_rect.y + popup_height - 80, button_width, button_height)
        minus_button_rect = pygame.Rect(plus_button_rect.x + button_width + button_spacing, popup_rect.y + popup_height - 80, button_width, button_height)
        done_button_rect = pygame.Rect(minus_button_rect.x + button_width + button_spacing, popup_rect.y + popup_height - 80, button_width * 2 + button_spacing, button_height)

        # Draw the buttons
        pygame.draw.rect(screen, BUTTON_COLOR, plus_button_rect,1, border_radius=5)
        pygame.draw.rect(screen, BUTTON_COLOR, minus_button_rect,1, border_radius=5)
        pygame.draw.rect(screen, BUTTON_COLOR, done_button_rect,1, border_radius=5)

        # Render the +, -, and Done text on the buttons
        plus_button_text = font.render("+", True, TEXT_COLOR)
        minus_button_text = font.render("-", True, TEXT_COLOR)
        done_button_text = font.render("Done", True, TEXT_COLOR)
        screen.blit(plus_button_text, (plus_button_rect.x + (button_width - plus_button_text.get_width()) // 2, plus_button_rect.y + (button_height - plus_button_text.get_height()) // 2))
        screen.blit(minus_button_text, (minus_button_rect.x + (button_width - minus_button_text.get_width()) // 2, minus_button_rect.y + (button_height - minus_button_text.get_height()) // 2))
        screen.blit(done_button_text, (done_button_rect.x + (done_button_rect.width - done_button_text.get_width()) // 2, done_button_rect.y + (button_height - done_button_text.get_height()) // 2))

        # Handle button clicks (single press)
        mouse_pos = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0]:  # Left mouse button is pressed
            if not self.mouse_pressed:  # Trigger only once
                self.mouse_pressed = True

                # Handle Plus button click
                if plus_button_rect.collidepoint(mouse_pos):
                    self.selected_quantity += 1

                # Handle Minus button click
                if minus_button_rect.collidepoint(mouse_pos):
                    self.selected_quantity = max(1, self.selected_quantity - 1)

                # Handle Done button click
                if done_button_rect.collidepoint(mouse_pos):
                    # Add item to cart and close popup
                    self.cart_items.append({
                        "name": self.selected_product["name"],
                        "quantity": self.selected_quantity,
                        "price": self.selected_product["price"] * self.selected_quantity,
                    })
                    self.selected_product = None  # Close the popup

        # Reset mouse_pressed when the mouse button is released
        if not pygame.mouse.get_pressed()[0]:
            self.mouse_pressed = False



# Run the game loop as before
app = SockioApp()
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    app.handle_scroll()  # Handle scroll bar interaction
    app.draw()
    pygame.display.update()
