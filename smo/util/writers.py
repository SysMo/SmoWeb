from docutils.writers import html4css1
from docutils import nodes
import sys
import os
import re
import urllib
try: # check for the Python Imaging Library
    import PIL.Image
except ImportError:
    try:  # sometimes PIL modules are put in PYTHONPATH's root
        import Image
        class PIL(object): pass  # dummy wrapper
        PIL.Image = Image
    except ImportError:
        PIL = None

class SmoHTMLWriter(html4css1.Writer):
    """
    Custom HTML writer
    """
    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = SmoHTMLTranslator

class SmoHTMLTranslator(html4css1.HTMLTranslator):
    """
    Custom translator of restructured text into HTML
    """
    ##### Add target = "_self" attribute to links
    def visit_reference(self, node):
        atts = {'class': 'reference', 'target': '_self'}
        if 'refuri' in node:
            atts['href'] = node['refuri']
            if ( self.settings.cloak_email_addresses
                 and atts['href'].startswith('mailto:')):
                atts['href'] = self.cloak_mailto(atts['href'])
                self.in_mailto = True
            atts['class'] += ' external'
        else:
            assert 'refid' in node, \
                   'References must have "refuri" or "refid" attribute.'
            atts['href'] = '#' + node['refid']
            atts['class'] += ' internal'
        if not isinstance(node.parent, nodes.TextElement):
            assert len(node) == 1 and isinstance(node[0], nodes.image)
            atts['class'] += ' image-reference'
        self.body.append(self.starttag(node, 'a', '', **atts))

    def depart_reference(self, node):
        self.body.append('</a>')
        if not isinstance(node.parent, nodes.TextElement):
            self.body.append('\n')
        self.in_mailto = False
    #####
    
    ##### Wraps SVG images into an <img> element, instead of an <object> elment
    def visit_image(self, node):
        atts = {}
        uri = node['uri']
        # place SVG and SWF images in <img> and <object> elements, respectively
        types = {'.svg': 'image/svg+xml',
                 '.swf': 'application/x-shockwave-flash'}
        ext = os.path.splitext(uri)[1].lower()
        if (ext == '.svg'):
            atts['src'] = uri
        elif (ext == '.swf'):
            atts['data'] = uri
            atts['type'] = types[ext]
        else:
            atts['src'] = uri
            atts['alt'] = node.get('alt', uri)
        
        # image size
        if 'width' in node:
            atts['width'] = node['width']
        if 'height' in node:
            atts['height'] = node['height']
        if 'scale' in node:
            if (PIL and not ('width' in node and 'height' in node)
                and self.settings.file_insertion_enabled):
                imagepath = urllib.url2pathname(uri)
                try:
                    img = PIL.Image.open(
                            imagepath.encode(sys.getfilesystemencoding()))
                except (IOError, UnicodeEncodeError):
                    pass # TODO: warn?
                else:
                    self.settings.record_dependencies.add(
                        imagepath.replace('\\', '/'))
                    if 'width' not in atts:
                        atts['width'] = '%dpx' % img.size[0]
                    if 'height' not in atts:
                        atts['height'] = '%dpx' % img.size[1]
                    del img
            for att_name in 'width', 'height':
                if att_name in atts:
                    match = re.match(r'([0-9.]+)(\S*)$', atts[att_name])
                    assert match
                    atts[att_name] = '%s%s' % (
                        float(match.group(1)) * (float(node['scale']) / 100),
                        match.group(2))
        style = []
        for att_name in 'width', 'height':
            if att_name in atts:
                if re.match(r'^[0-9.]+$', atts[att_name]):
                    # Interpret unitless values as pixels.
                    atts[att_name] += 'px'
                style.append('%s: %s;' % (att_name, atts[att_name]))
                del atts[att_name]
        if style:
            atts['style'] = ' '.join(style)
        if (isinstance(node.parent, nodes.TextElement) or
            (isinstance(node.parent, nodes.reference) and
             not isinstance(node.parent.parent, nodes.TextElement))):
            # Inline context or surrounded by <a>...</a>.
            suffix = ''
        else:
            suffix = '\n'
        if 'align' in node:
            atts['class'] = 'align-%s' % node['align']
        self.context.append('')
        if (ext == '.swf'):
            # do NOT use an empty tag: incorrect rendering in browsers
            self.body.append(self.starttag(node, 'object', suffix, **atts) +
                             node.get('alt', uri) + '</object>' + suffix)
        elif (ext == '.svg'):
            self.body.append(self.starttag(node, 'img', suffix, **atts) +
                             '</img>' + suffix)
        else:
            self.body.append(self.emptytag(node, 'img', suffix, **atts))

    def depart_image(self, node):
        self.body.append(self.context.pop())   
    
