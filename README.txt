collective.plonefinder
======================


Ajax popup to reference plone contents.

This code is an extraction of plonearticle explorer for referencables contents

The intent is to make it usable in different situations :

- for referencable fields inside AT edit forms

- to store selected contents in zope3 forms (portlet forms as example)

- for collective.ckeditor or any possible wysiwyg editor for referencing images or contents inside a rich text field,
  it's also possible to upload files / images and create folders with this product (big part of code taken from collective.uploadify)

- for links fields (as remoteUrl in ATLink) to reference internal links   

This work has been started at Ingeniweb in 2007 by Christophe Bosse & Jean-mat Grimaldi for PloneArticle product. 


How to use it as reference widget :
===================================

A reference widget for zope3 forms is available inside this product.

The widget can be used to store objects references in a sequence field.

Example of use in a portlet form for a field named target_contents::

    from collective.plonefinder.widgets.referencewidget import FinderSelectWidget

    target_contents = schema.Tuple (title=u"Browse for contents",
                                    description =u"Choose contents to display "
                                                  "with a plone finder window. ",
                                    required = False,
                                    default= ()
                                    )

    form_fields['target_contents'].custom_widget = FinderSelectWidget

Example of use for images referencing::

    from collective.plonefinder.widgets.referencewidget import FinderSelectImageWidget

    target_images = schema.Tuple (title=u"Browse for images",
                                  description =u"Choose images to display "
                                                 "with a plone finder window. "
                                                 "You can select different image sizes. "
                                                 "You can upload new images. ",
                                  required = False,
                                  default= ()
                                  )

    form_fields['target_images'].custom_widget = FinderSelectImageWidget
   

How to use it in wysiwyg editor  :
==================================
   
See the collective.ckeditor product as example.

You can easily use it with another editor.


Todo :
======

- i18N support

- Ajax opening/moving and all window effects inside the same browser window (in progress)

- Improve some reference widget options (add option to hide or show selected items in browser)

- New zope3 widget to store urls (for a string field)


Authors :
=========

Jean-mat Grimaldi - Alter Way Solutions

Code repository :
=================

https://svn.plone.org/svn/collective/collective.plonefinder/trunk

Support :
=========

- Questions and comments to support@ingeniweb.com


