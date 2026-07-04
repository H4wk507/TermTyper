options:
    easier mode: 5 letter words max
    hard mode: any length words
    punctuation
    numbers
    quotes

- spaces wont print when inside a word

- calculate accuracy: (done)
    1.
        Hold chars_typed var, which stores how many chars were typed
        deletion does not change this variable, every time we hit a 
        valid key it increases by 1.
        mistyped_chars = chars_typed - len(current)

        Problems:
            target = abc
            user types adc and corrects to abc
            chars_typed = 5, len(current) = 3
            mistyped_chars = 2 which is wrong

            Artifically boost accuracy by typing valid chars, deleting, 
            and typing again.

    2.
        Hold text_ptr which points to char in the text.
        If user types a char, check if its the same as text_ptr
        if it is not update mistype_chars
        
accuracy = valid_chars / chars_typed
Make accuracy show up at the end; calculating it in real time is too 
hard. accuracy = (len(current) - mistyped) / len(current) 
               or len(text) (it's the same thing at the end).


move from curses to urwid (?)
