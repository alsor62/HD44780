################################################################################
# HD44780
#
# Created: 2016-03-18 22:56:10.817946
#
################################################################################
import hwtimers

### BIT PATTERNS ###

# Commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# Flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# Flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# Flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00

# Flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# Flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00

# Flags for RS pin modes
RS_INSTRUCTION = 0x00
RS_DATA = 0x01


### NAMEDTUPLES ###

# PinConfig = namedtuple('PinConfig', 'rs rw e d0 d1 d2 d3 d4 d5 d6 d7 mode')
# LCDConfig = namedtuple('LCDConfig', 'rows cols dotsize')


### ENUMS ###

# class Alignment():
#     left = LCD_ENTRYLEFT
#     right = LCD_ENTRYRIGHT


# class ShiftMode():
#     cursor = LCD_ENTRYSHIFTDECREMENT
#     display = LCD_ENTRYSHIFTINCREMENT


# class CursorMode():
#     hide = LCD_CURSOROFF | LCD_BLINKOFF
#     line = LCD_CURSORON | LCD_BLINKOFF
#     blink = LCD_CURSOROFF | LCD_BLINKON


### MAIN ###

# class PinConfig():
    
#     def __init__(self,rs, rw, e, d0, d1, d2, d3, d4, d5, d6, d7):
#         self.rs=rs
#         self.rw=rw
#         self.e=e
        
    

class CharLCD():

    # Init, setup, teardown

    def __init__(self, pin_rs=15, pin_rw=18, pin_e=16, pins_data=[21, 22, 23, 24],
                       cols=20, rows=4, dotsize=8):
        """
        Character LCD controller.

        The default pin numbers are based on the BOARD numbering scheme (1-26).

        You can save 1 pin by not using RW. Set ``pin_rw`` to ``None`` if you
        want this.

        Args:
            pin_rs:
                Pin for register select (RS). Default: 15.
            pin_rw:
                Pin for selecting read or write mode (R/W). Set this to
                ``None`` for read only mode. Default: 18.
            pin_e:
                Pin to start data read or write (E). Default: 16.
            pins_data:
                List of data bus pins in 8 bit mode (DB0-DB7) or in 8 bit mode
                (DB4-DB7) in ascending order. Default: [21, 22, 23, 24].
            numbering_mode:
                Which scheme to use for numbering of the GPIO pins, either
                ``GPIO.BOARD`` or ``GPIO.BCM``.  Default: ``GPIO.BOARD`` (1-26).
            rows:
                Number of display rows (usually 1, 2 or 4). Default: 4.
            cols:
                Number of columns per row (usually 16 or 20). Default 20.
            dotsize:
                Some 1 line displays allow a font height of 10px.
                Allowed: 8 or 10. Default: 8.

        Returns:
            A :class:`CharLCD` instance.

        """
#         assert dotsize in [8, 10], 'The ``dotsize`` argument should be either 8 or 10.'

        # Set attributes

        if len(pins_data) == 4:  # 4 bit mode
            self.data_bus_mode = LCD_4BITMODE
            block1 = [None] * 4
        elif len(pins_data) == 8:  # 8 bit mode
            self.data_bus_mode = LCD_8BITMODE
            block1 = pins_data[:4]
#         else:
#             raise OSError('There should be exactly 4 or 8 data pins.')
        block2 = pins_data[-4:]
#         self.pins = PinConfig(rs=pin_rs, rw=pin_rw, e=pin_e,
#                               d0=block1[0], d1=block1[1], d2=block1[2], d3=block1[3],
#                               d4=block2[0], d5=block2[1], d6=block2[2], d7=block2[3])
        self.pins=(pin_rs,pin_rw,pin_e,block1[0], block1[1], block1[2], block1[3],
                             block2[0], block2[1], block2[2], block2[3])
        self.lcd = (rows, cols, dotsize)

        # Setup GPIO
#         GPIO.setmode(self.numbering_mode)
        for pin in self.pins:
            if pin!=None:
                pinMode (pin,OUTPUT)

        # Setup initial display configuration
        displayfunction = self.data_bus_mode | LCD_5x8DOTS
        if rows == 1:
            displayfunction |= LCD_1LINE
        elif rows in [2, 4]:
            # LCD only uses two lines on 4 row displays
            displayfunction |= LCD_2LINE
        if dotsize == 10:
            # For some 1 line displays you can select a 10px font.
            displayfunction |= LCD_5x10DOTS

        # Create content cache
        self._content = [[0x20] * cols for _ in range(rows)]

        # Initialization
        sleep(50)
        digitalWrite(self.pins.rs, 0)
        digitalWrite(self.pins.e, 0)
        if self.pins.rw is not None:
            digitalWrite(self.pins.rw, 0)

        # Choose 4 or 8 bit mode
        if self.data_bus_mode == LCD_4BITMODE:
            # Hitachi manual page 46
            self._write4bits(0x03)
            sleep(4.5)
            self._write4bits(0x03)
            sleep(4.5)
            self._write4bits(0x03)
            hwtimers.sleep(100)
            self._write4bits(0x02)
        elif self.data_bus_mode == LCD_8BITMODE:
            # Hitachi manual page 45
            self._write8bits(0x30)
            sleep(4.5)
            self._write8bits(0x30)
            hwtimers.sleep(100)
            self._write8bits(0x30)
#         else:
#             raise ValueError('Invalid data bus mode: {}'.format(self.data_bus_mode))

        # Write configuration to display
        self.command(LCD_FUNCTIONSET | displayfunction)
        hwtimers.sleep(50)

        # Configure display mode
        self._display_mode = LCD_DISPLAYON
        self._cursor_mode = LCD_CURSOROFF | LCD_BLINKOFF
        self.command(LCD_DISPLAYCONTROL | self._display_mode | self._cursor_mode)
        hwtimers.sleep(50)

        # Clear display
        self.clear()

        # Configure entry mode
        self._text_align_mode = LCD_ENTRYLEFT
        self._display_shift_mode = LCD_ENTRYSHIFTDECREMENT
        self._cursor_pos = (0, 0)
        self.command(LCD_ENTRYMODESET | self._text_align_mode | self._display_shift_mode)
        hwtimers.sleep(50)

#     def close(self, clear=False):
#         if clear:
#             self.clear()
#         GPIO.cleanup()

    # Properties

    def _get_cursor_pos(self):
        return self._cursor_pos

    def _set_cursor_pos(self, value):
#         if not hasattr(value, '__getitem__') or len(value) != 2:
#             raise ValueError('Cursor position should be determined by a 2-tuple.')
        if value[0] not in range(self.lcd.rows) or value[1] not in range(self.lcd.cols):
            msg = 'Cursor position {pos!r} invalid on a {lcd.rows}x{lcd.cols} LCD.'
#             raise ValueError(msg.format(pos=value, lcd=self.lcd))
        row_offsets = [0x00, 0x40, self.lcd.cols, 0x40 + self.lcd.cols]
        self._cursor_pos = value
        self.command(LCD_SETDDRAMADDR | row_offsets[value[0]] + value[1])
        hwtimers.sleep(50)

#     cursor_pos = property(_get_cursor_pos, _set_cursor_pos,
#             doc='The cursor position as a 2-tuple (row, col).')

#     def _get_text_align_mode(self):
#         try:
#             return Alignment[self._text_align_mode]
#         except ValueError:
#             raise ValueError('Internal _text_align_mode has invalid value.')

    def _set_text_align_mode(self, value):
#         if not value in Alignment:
#             print ('ValueError(Cursor move mode must be of ``Alignment`` type.')
        self._text_align_mode = int(value)
        self.command(LCD_ENTRYMODESET | self._text_align_mode | self._display_shift_mode)
        hwtimers.sleep(50)

#     text_align_mode = property(_get_text_align_mode, _set_text_align_mode,
#             doc='The text alignment (``Alignment.left`` or ``Alignment.right``).')

#     def _get_write_shift_mode(self):
#         try:
#             return ShiftMode[self._display_shift_mode]
#         except ValueError:
#             print ('ValueError(Internal _display_shift_mode has invalid value.)')

    def _set_write_shift_mode(self, value):
#         if not value in ShiftMode:
#             raise ValueError('Write shift mode must be of ``ShiftMode`` type.')
        self._display_shift_mode = int(value)
        self.command(LCD_ENTRYMODESET | self._text_align_mode | self._display_shift_mode)
        hwtimers.sleep(50)

#     write_shift_mode = property(_get_write_shift_mode, _set_write_shift_mode,
#             doc='The shift mode when writing (``ShiftMode.cursor`` or ``ShiftMode.display``).')

    def _get_display_enabled(self):
        return self._display_mode == LCD_DISPLAYON

    def _set_display_enabled(self, value):
        if value:
            self._display_mode = LCD_DISPLAYON 
        else:
            self._display_mode = LCD_DISPLAYOFF
        self.command(LCD_DISPLAYCONTROL | self._display_mode | self._cursor_mode)
        hwtimers.sleep(50)

#     display_enabled = property(_get_display_enabled, _set_display_enabled,
#             doc='Whether or not to display any characters.')

#     def _get_cursor_mode(self):
#         try:
#             return CursorMode[self._cursor_mode]
#         except ValueError as e:
#             print (e,'Internal _cursor_mode has invalid value.')

    def _set_cursor_mode(self, value):
#         if not value in CursorMode:
#             print ('ValueError(Cursor mode must be of ``CursorMode`` type.)')
        self._cursor_mode = int(value)
        self.command(LCD_DISPLAYCONTROL | self._display_mode | self._cursor_mode)
        hwtimers.sleep(50)

#     cursor_mode = property(_get_cursor_mode, _set_cursor_mode,
#             doc='How the cursor should behave (``CursorMode.hide``, ' +
#                                    '``CursorMode.line`` or ``CursorMode.blink``).')

    # High level commands

    def write_string(self, value):
        """Write the specified unicode string to the display.

        To control multiline behavior, use newline (\n) and carriage return
        (\r) characters.

        Lines that are too long automatically continue on next line.

        Make sure that you're only passing unicode objects to this function. If
        you're dealing with bytestrings (the default string type in Python 2),
        convert it to a unicode object using the ``.decode(encoding)`` method
        and the appropriate encoding. Example for UTF-8 encoded strings:

        .. code::

            >>> bstring = 'Temperature: 30ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ°C'
            >>> bstring
            'Temperature: 30\xc2\xb0C'
            >>> bstring.decode('utf-8')
            u'Temperature: 30\xb0C'

        Only characters with an ``ord()`` value between 0 and 255 are currently
        supported.

        """
        for char in value:
            # Write regular chars
            if char not in '\n\r':
                self.write(ord(char))
                continue
            # Handle newlines and carriage returns
            row, col = self.cursor_pos
            if char == '\n':
                if row < self.lcd.rows - 1:
                    self.cursor_pos = (row + 1, col)
                else:
                    self.cursor_pos = (0, col)
            elif char == '\r':
                if self.text_align_mode is LCD_ENTRYLEFT:
                    self.cursor_pos = (row, 0)
                else:
                    self.cursor_pos = (row, self.lcd.cols - 1)

    def clear(self):
        """Overwrite display with blank characters and reset cursor position."""
        self.command(LCD_CLEARDISPLAY)
        self._cursor_pos = (0, 0)
        self._content = [[0x20] * self.lcd.cols for _ in range(self.lcd.rows)]
        sleep(2)

    def home(self):
        """Set cursor to initial position and reset any shifting."""
        self.command(LCD_RETURNHOME)
        self._cursor_pos = (0, 0)
        sleep(2)

    def shift_display(self, amount):
        """Shift the display. Use negative amounts to shift left and positive
        amounts to shift right."""
        if amount == 0:
            return
        if amount >0 :
            direction = LCD_MOVERIGHT 
        else :
            direction = LCD_MOVELEFT
        for i in range(abs(amount)):
            self.command(LCD_CURSORSHIFT | LCD_DISPLAYMOVE | direction)
            hwtimers.sleep(50)

    def create_char(self, location, bitmap):
        """Create a new character.

        The HD44780 supports up to 8 custom characters (location 0-7).

        Args:
            location:
                The place in memory where the character is stored. Values need
                to be integers between 0 and 7.
            bitmap:
                The bitmap containing the character. This should be a tuple of
                8 numbers, each representing a 5 pixel row.

        Raises:
            AssertionError:
                Raised when an invalid location is passed in or when bitmap
                has an incorrect size.

        Example::

            >>> smiley = (
            ...     0b00000,
            ...     0b01010,
            ...     0b01010,
            ...     0b00000,
            ...     0b10001,
            ...     0b10001,
            ...     0b01110,
            ...     0b00000,
            ... )
            >>> lcd.create_char(0, smiley)

        """
#         assert 0 <= location <= 7, 'Only locations 0-7 are valid.'
#         assert len(bitmap) == 8, 'Bitmap should have exactly 8 rows.'

        # Store previous position
        pos = self.cursor_pos

        # Write character to CGRAM
        self.command(LCD_SETCGRAMADDR | location << 3)
        for row in bitmap:
            self._send(row, RS_DATA)

        # Restore cursor pos
        self.cursor_pos = pos

    # Mid level commands

    def command(self, value):
        """Send a raw command to the LCD."""
        self._send(value, RS_INSTRUCTION)

    def write(self, value):
        """Write a raw byte to the LCD."""

        # Get current position
        row, col = self._cursor_pos

        # Write byte if changed
        if self._content[row][col] != value:
            self._send(value, RS_DATA)
            self._content[row][col] = value  # Update content cache
            unchanged = False
        else:
            unchanged = True

        # Update cursor position.
        if self.text_align_mode is LCD_ENTRYLEFT:
            if col < self.lcd.cols - 1:
                # No newline, update internal pointer
                newpos = (row, col + 1)
                if unchanged:
                    self.cursor_pos = newpos
                else:
                    self._cursor_pos = newpos
            else:
                # Newline, reset pointer
                if row < self.lcd.rows - 1:
                    self.cursor_pos = (row + 1, 0)
                else:
                    self.cursor_pos = (0, 0)
        else:
            if col > 0:
                # No newline, update internal pointer
                newpos = (row, col - 1)
                if unchanged:
                    self.cursor_pos = newpos
                else:
                    self._cursor_pos = newpos
            else:
                # Newline, reset pointer
                if row < self.lcd.rows - 1:
                    self.cursor_pos = (row + 1, self.lcd.cols - 1)
                else:
                    self.cursor_pos = (0, self.lcd.cols - 1)

    # Low level commands

    def _send(self, value, mode):
        """Send the specified value to the display with automatic 4bit / 8bit
        selection. The rs_mode is either ``RS_DATA`` or ``RS_INSTRUCTION``."""

        # Choose instruction or data mode
        digitalWrite(self.pins.rs, mode)

        # If the RW pin is used, set it to low in order to write.
        if self.pins.rw is not None:
            digitalWrite(self.pins.rw, 0)

        # Write data out in chunks of 4 or 8 bit
        if self.data_bus_mode == LCD_8BITMODE:
            self._write8bits(value)
        else:
            self._write4bits(value >> 4)
            self._write4bits(value)

    def _write4bits(self, value):
        """Write 4 bits of data into the data bus."""
        for i in range(4):
            bit = (value >> i) & 0x01
            digitalWrite(self.pins[i + 7], bit)
        self._pulse_enable()

    def _write8bits(self, value):
        """Write 8 bits of data into the data bus."""
        for i in range(8):
            bit = (value >> i) & 0x01
            digitalWrite(self.pins[i + 3], bit)
        self._pulse_enable()

    def _pulse_enable(self):
        """Pulse the `enable` flag to process data."""
        digitalWrite(self.pins.e, 0)
        hwtimers.sleep(1)
        digitalWrite(self.pins.e, 1)
        hwtimers.sleep(1)
        digitalWrite(self.pins.e, 0)
        hwtimers.sleep(100)  # commands need > 37us to settle
        
        
lcd = CharLCD(pin_rs=8, pin_rw=None, pin_e=9, pins_data=[4,5,6,7],
                       cols=16, rows=2)
lcd.write_string('Hello world!')