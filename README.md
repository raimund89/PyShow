# PyShow
Make your presentations scriptable! This Python and PyQt5 based slide show IDE lets you write your slide shows using an easy-to-use scripting language. This scripting language allows you more control over your presentation flow, removes the borders between slides and enables automatic generation of your presentation using any language you want!

# Current development status
I'm slowly developing this software in my free time. No guarantees that a new commit won't break the software :) Stick to the releases if you want any kind of stability, although I also cannot guarantee that :P

# Features for future implementation
- Include directive, to for example include a template file
- Support for URLs for images, gifs, videos, audio, includes, etc.
- Compilation of presentation into a standalone file (exe/py?)
- Support for plot generation from data
- Functions, for repetative actions
- Re-usable resources (images, videos, etc.) so loading is only done once
- Notes for presenter when using double screen
- Quick navigation (for example for Q&A session)

# Detailed todo list
- Rewrite the bullet list code. Implement several 'default' bullet types (dot, square, arrow, etc) to choose from, or allow a user to use an image. Also implement nested lists.
- Implement a project window, with all files available (scripts, images, videos, etc)
- Make a good overview of the file structure of a project file
- Implement a console window that shows errors
- Highlight the right line of code for errors. Probably for this the entire parsing code needs to be redesigned, maybe self-written
- A self-written parsing code has the advantage of attaching code functions to every part, increasing rendering speed
- Code-completion, also for string parameters (like the object name, image file, font list, etc)
- Implement inline comments
- When a line is selected in the editor, show a bounding-box around the item changed in the current line
- Add font browser
- Out-of-bounds warnings for objects
- When a resource-line is selected, show a preview of the resource instead of the presentation
- Scrollbar style is no good
- Do some timing tests on the drawing scripts, see which things can be faster
- Add a white app icon, and choose depending on the appbar color
- Allow PyShowIcon to store several sizes of the app icon