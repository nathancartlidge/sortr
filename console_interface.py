"""Functions to enable an interactive console"""

from blessed import Terminal


def get_option(term: Terminal=None, title="Menu", subtitle=None, options=None) -> int:
    """
    Provides a menu to select from a list of options
    Note that this function does not currently have protection against very
    small screen sizes, and as such they may cause issues
    """
    if not term:
        term = Terminal()

    if not options:
        # if no options are provided, there can be no menu displayed
        return None

    def redraw_screen():
        """
        re-draws the basic elements of the menu,
        to ensure resize does not break functionality
        """
        offset = 0
        print(term.clear)

        if title: # print title, if any
            print(term.move(0, 0) + term.bold(title))
            offset += 1

        if subtitle: # print subtitle, if any
            print(subtitle)
            offset += 1

        for i, option in enumerate(options): # print options list
            print(f"  {i+1}: {option}")

        return offset

    def highlight_option(y_function, option):
        """short function to highlight an option"""
        print(y_function() + f"{term.reverse}> {option + 1}: {options[option]} <{term.normal}")

    def unhighlight_option(y_function, option):
        """short function to un-highlight an option"""
        print(y_function() + f"  {option + 1}: {options[option]}   ")

    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        # term.fullscreen() - use secondary screen buffer
        # term.cbreak() - capture all keyboard input
        # term.hidden_cursor() - hide cursor
        cur_option = 0
        output = None
        offset = redraw_screen()
        get_y = lambda : term.move(offset + cur_option, 0) # short function to handle offsets

        y_height = term.height

        while True:
            if term.height != y_height: # redraw if resized
                # note this is badly implemented, as windows does not support sending the resize signal
                offset = redraw_screen()
                y_height = term.height

            highlight_option(get_y, cur_option)
            key = term.inkey()
            unhighlight_option(get_y, cur_option)
            # un-highlight, ready for next item to be higlighted
            # this process could probably be cleaned up a little

            if key.is_sequence: # arrow keys are encoded as a sequence of keycodes under the hood
                if key.name == "KEY_UP":
                    cur_option = (cur_option - 1) % len(options)
                if key.name == "KEY_DOWN":
                    cur_option = (cur_option + 1) % len(options)
                if key.name == "KEY_ENTER":
                    output = cur_option
                    break

            elif 48 < ord(key) < 58: # extract number keys
                if int(key) <= len(options):
                    cur_option = int(key) - 1

            elif key.lower() == "q": # quit option
                break

    if output is None:
        result = "None"
    else:
        result = options[output]

    print(term.bold(title) + " - " + term.blue(result)) # print selection to console
    return output


def get_input(term: Terminal=None, title="Input", prompt="> ") -> str:
    """Provides a menu to input strings"""
    if not term:
        term = Terminal()

    print(term.bold(title))
    user_input = input(prompt)

    print(term.move_up + term.move_x(0) + term.clear_eol # clear input line
          + term.move_up + term.move_x(0) + term.clear_eol
          + term.bold(title) + " " + term.blue(prompt + user_input)) # re-print result

    return user_input


def get_bool(term: Terminal=None, title="Input", options=None) -> bool:
    """Provides a menu to select a boolean option"""
    if not term:
        term = Terminal()

    if options is None:
        options = ["No", "Yes"]

    print(term.bold(title))
    print()

    with term.cbreak(), term.hidden_cursor(), term.location():
        # term.cbreak() - capture all keyboard input

        false_selected = f"{term.move_up}{term.move_x(0)}{term.reverse}{term.red} {options[0]} {term.normal}  {options[1]}  "
        true_selected = f"{term.move_up}{term.move_x(0)} {options[0]}  {term.reverse}{term.green} {options[1]} {term.normal} "

        cur_option = 0
        output = None

        while True:
            print(true_selected if cur_option else false_selected)
            key = term.inkey()

            if key.is_sequence: # arrow keys are encoded as a sequence of keycodes under the hood
                if key.name == "KEY_LEFT":
                    cur_option = 0
                if key.name == "KEY_RIGHT":
                    cur_option = 1
                if key.name == "KEY_ENTER":
                    output = cur_option == 1
                    break
            elif key.lower() in ("y", "t"):
                cur_option = 0
            elif key.lower() in ("n", "f"):
                cur_option = 1
            elif key.lower() == "q":
                output = None
                break

    if output is None:
        result = "None"
    else:
        result = options[output]

    print(term.move_up + term.move_x(0) + term.clear_eol # clear input line
          + term.move_up + term.move_x(0) + term.clear_eol
          + term.bold(title) + " - " + term.blue(result)) # re-print result

    return output
