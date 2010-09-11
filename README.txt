collective.plonefinder
======================

Ajax popup to browse and select plone contents.

This code is an extraction with some refactoring, of PloneArticle explorer used for referencables proxies.

The intent is to make it usable in different situations :

- to store selected contents in zope3 forms (portlet forms as example)

- for collective.ckeditor or any possible wysiwyg editor for referencing images or contents inside a rich text field,
  it's also possible to upload files / images and create folders with this product (dependency to collective.quickupload)

- for referencable fields inside AT edit forms

- for links fields (as remoteUrl in ATLink) to reference internal links   

This work has been started at Ingeniweb in 2007 by Christophe Bosse (for the jQuery code) & Jean-mat Grimaldi (everything else) for PloneArticle product. 


Requirements :
==============

* Plone3 and more (tested under Plone 3.3.5 and Plone4)

Installation :
==============

* Nothing to do if you have installed collective.ckeditor (plone4 only at this time)

* Otherwise install it as any zope package using buildout :

  - add collective.plonefinder in your eggs section

  - add collective.plonefinder in your zcml section

  - bin/buildout

Nothing else. 

How to use it as a reference widget in zope3 forms :
====================================================

A reference widget for zope3 forms (zope.app.form) is provided with this product.

The widget can be used to store objects references in a sequence field.

Example of use in a portlet form for a Tuple field named target_contents::

    from collective.plonefinder.widgets.referencewidget import FinderSelectWidget

    target_contents = schema.Tuple (title=u"Browse for contents",
                                    description =u"Choose contents to display "
                                                  "with a plone finder window. ",
                                    default= ()
                                    )

    form_fields['target_contents'].custom_widget = FinderSelectWidget

You can use the FinderSelectWidget with some properties set using the update 
method in your AddForm or EditForm, example for a portlet AddForm::

    class AddForm(base.AddForm):
        """Portlet add form.
        """
        form_fields = form.Fields(IReferencesPortlet)
        form_fields['targets'].custom_widget = FinderSelectWidget
        label = u"Add References Portlet"
    
        def update(self) :
            super(AddForm, self).update()
            self.widgets['targets'].typeview = 'image'
            self.widgets['targets'].forcecloseoninsert = 1
            
        def create(self, data):
            return Assignment(**data)

If you want, you can also pass a context as base for the widget, to get the current 
or parent folder open in the finder. Example in a portlet using the update
method::

        assignment = aq_parent(aq_inner(self.context))
        self.widgets['targets'].base = aq_parent(aq_inner(assignment))

There are also two customized Widget for files and images. Look at the code
to create your own specific widget.

Example of code for files referencing with files upload support::

    from collective.plonefinder.widgets.referencewidget import FinderSelectFileWidget

    target_files = schema.Tuple (title=u"Browse for images",
                                  description =u"Choose files to display "
                                                 "with a plone finder window. "
                                                 "You can upload new files. ",
                                  default= ()
                                  )

    form_fields['target_files'].custom_widget = FinderSelectFileWidget

Example of code for images referencing with images upload support::

    from collective.plonefinder.widgets.referencewidget import FinderSelectImageWidget

    target_images = schema.Tuple (title=u"Browse for images",
                                  description =u"Choose images to display "
                                                 "with a plone finder window. "
                                                 "You can select different image sizes. "
                                                 "You can upload new images. ",
                                  default= ()
                                  )

    form_fields['target_images'].custom_widget = FinderSelectImageWidget

Note that in this last case the data store image uid and image thumb size like this::

    '%s/%s' %(image.UID(), thumb_size_extension)

thumb_size_extension could be 'image_thumb' or 'image_preview' ...

So use something like this to display a referenced image ::

    '<img src="%s/resolveuid/%s/%s" />' %(portal_url, data.split('/')[0], data.split('/')[1])
   

How to use it in a wysiwyg editor  :
====================================

The more easy way is creating a specific view,
because you will often need to override the javascript method to select objects,
and because each editor has its specific mechanism to dialog with browser.

See collective.ckeditor package as example.


Todo :
======

- Functional doctests

- i18N support

- Finder improvements :

  - Ajax opening/moving/resizing and all window effects inside the same browser window (in progress, need some js refactoring)
  
  - improve contextual actions menu (change workflow state, rename, delete, copy, paste ...)
  
  - add a finder menu action to show/hide the current selection list in right panel
  
  - remove items from selection list in finder window

- Improve zope3 reference widget properties

  - add option to hide/show or just mark selected items in finder browsing results (just need to store the finder blacklist in session)
  
  - add option to set a specific catalog query stored in session
  
  - add option to change finder catalog.


- New zope3 widget to store urls (for a string field)

- ATPloneFinderWidget for Reference fields (not a big challenge, just need to use ATReferenceBrowserWidget as base to start the work)

- ATLinkWidget to store internal links


Any contribution is welcome, contact support@ingeniweb.com.

Authors :
=========

Jean-mat Grimaldi - Alter Way Solutions

Code repository :
=================

https://svn.plone.org/svn/collective/collective.plonefinder/trunk

Support :
=========

- Questions and comments to support@ingeniweb.com


