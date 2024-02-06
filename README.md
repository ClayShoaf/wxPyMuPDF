# wxPyMuPDF
A pdf reader written in python, using wxPython and PyMuPDF - with vim keybindings

The name could use a little work, but I wasn't sure if I was actually going to make this public. This is a project that I was working on to help me with underwriting. I have since been told that I am not allowed to use this software at my company, so I figured, why let weeks worth of work go to waste? Might as well just release it.

The current options for PDF readers were missing some key features. These are the things I was working on (though most of my time has been spent optimizing page rendering):

- [x] rotate individual pages, moving landscape pages to their own line, so you don't have to zoom/scroll so much
- [x] vim keys navigation
- [x] keyboard shortcuts for switching between single/two page mode
- [ ] image classification for recognizing standard forms
- [ ] overlaying standard forms to highlight user data, using image registration
- [ ] using OCR in combination with an object detection model to more accurately pull data from forms.

### Navigation:
- h/j/k/l scroll
- d/u jump up or down (larger jumps than j/k)
- i/o zoom in/out
