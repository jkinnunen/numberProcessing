# NumberProcessing

This is an NVDA add-on to read automatically digit by digit any number of specified length (via settings or quick settings).

For example, with default minimum number length of 2, enabling digit processing you'll hear 42 as  4  2, 338 as 3  3  8, etc; setting number length on 4, instead, you'll hear 338 as usual, but 1337 as 1  3  3  7. 

In addition, from settings, you can also enable the autostart of digit processing for current profile.

Inspired by [an experimental work of Derek Riemer.][1]

Compatible with NVDA 2017.3 and above, download it [here.][2]

## Commands

* NVDA+shift+l (once): enable/disable digit processing;
* NVDA+shift+l (twice): open a dialog to change on the fly the minimum number of digits to process.

Note that shortcut is configurable by relative section in NVDA preferences.


[1]: https://github.com/derekriemer/phoneOpperationHelper
[2]: https://raw.githubusercontent.com/ABuffEr/numberProcessing/master/packages/numberProcessing-1.0-20191210-dev.nvda-addon
