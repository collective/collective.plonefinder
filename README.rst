======================
collective.plonefinder
======================

Ajax popup to browse and select plone contents, suitable to any
``plone.formilb`` form (portlets, control panels, ...)

This code is an extraction with some refactoring, of PloneArticle explorer used
for referencables proxies.

The intent is to make it usable in various situations:

- to store selected contents in ``plone.formlib`` based Plone forms (portlet or
  control panel forms as example)

- for ``collective.ckeditor`` or any possible wysiwyg editor for referencing
  images or contents inside a rich text field, it's also possible to upload
  files / images and create folders with this product (dependency to
  ``collective.quickupload``)

- for referencable fields inside AT edit forms (future)

- for links fields (as remoteUrl in ATLink) to reference internal links (future)

This work has been started at Ingeniweb in 2007 by Christophe Bosse (for the
jQuery code) and Jean-Mat Grimaldi (everything else) for PloneArticle product.

.. admonition::
   Plone add-ons developers only

   This is a component for Plone add-ons developers. Do not expect to add
   anything more in yous site if you install only this component to your Zope
   instance.

Requirements
============

* Plone (tested with Plone 3.3.5 and Plone 4)
* collective.quickupload

Installation
============

* Nothing to do if you have installed ``collective.ckeditor`` (Plone 4 only
  today)

* Otherwise install it as any Zope package using buildout :

  - add ``collective.plonefinder`` in your ``eggs`` section

  - add ``collective.plonefinder`` in your ``zcml`` section of the
    ``plone.recipe.zope2instance`` part definition if on Plone 3.0 or 3.1

  - Run ``bin/buildout``

Nothing else.

How to use it as a reference widget in formlib forms
====================================================

Basic usage
-----------

A reference widget for zope3 forms (zope.app.form) is provided with this product.

The widget can be used to store objects references in a sequence field.

Example of use in a portlet form for a Tuple field named target_contents::

    from collective.plonefinder.widgets.referencewidget import FinderSelectWidget

    target_contents = schema.Tuple(title=u"Browse for contents",
                                   description=(u"Choose contents to display "
                                                u"with a plone finder window."),
                                   default=()
                                   )

    form_fields['target_contents'].custom_widget = FinderSelectWidget

Tweaking some properties
------------------------

You can use the ``FinderSelectWidget`` with some properties set using the update
method in your ``AddForm`` or ``EditForm``. In example for a portlet ``AddForm``::

    class AddForm(base.AddForm):
        """Portlet add form.
        """
        form_fields = form.Fields(IReferencesPortlet)
        form_fields['targets'].custom_widget = FinderSelectWidget
        label = u"Add References Portlet"

        def update(self):
            super(AddForm, self).update()
            self.widgets['targets'].typeview = 'image'
            self.widgets['targets'].forcecloseoninsert = 1

        def create(self, data):
            return Assignment(**data)

If you want, you can also pass a context as base for the widget, to get the
current or parent folder open in the finder. Example in a portlet using the
``update`` method::

        assignment = aq_parent(aq_inner(self.context))
        self.widgets['targets'].base = aq_parent(aq_inner(assignment))

There are also two customized widgets for files and images. Look at the code to
create your own specific widget.

Example of code for files referencing with files upload support::

    from collective.plonefinder.widgets.referencewidget import FinderSelectFileWidget

    target_files = schema.Tuple(title=u"Browse for images",
                                description=(u"Choose files to display "
                                             u"with a plone finder window. "
                                             u"You can upload new files."),
                                default=()
                                )

    form_fields['target_files'].custom_widget = FinderSelectFileWidget

Example of code for images referencing with images upload support::

    from collective.plonefinder.widgets.referencewidget import FinderSelectImageWidget

    target_images = schema.Tuple (title=u"Browse for images",
                                  description=(u"Choose images to display "
                                               u"with a plone finder window. "
                                               u"You can select different image sizes. "
                                               u"You can upload new images."),
                                  default= ()
                                  )

    form_fields['target_images'].custom_widget = FinderSelectImageWidget

Note that in this last case the data store image uid and image thumb size like
this::

    '%s/%s' % (image.UID(), thumb_size_extension)

``thumb_size_extension`` could be ``'image_thumb'`` or ``'image_preview'`` ...

So use something like this to display a referenced image::

    uid, variant = data.split('/')
    '<img src="%s/resolveuid/%s/%s" />' % (portal_url, uid, variant)

Full list of customization attributes
-------------------------------------

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Attribute
     - Default value
     - Description
   * - ``finderlabel``
     - ``_(u'Browse for contents')``
     - Customize the title of the Browser window. i.e. ``"Find the pictures"``
   * - ``moveuplabel``
     - ``_(u'Move up')``
     - Label associated with the up arrow widget that raises the order of the
       reference. i.e. ``"Increase priority"``.
   * - ``movedownlabel``
     - ``_(u'Move down')``
     - Label associated with the down arrow widget that lowers the order of the
       reference. i.e. ``"Decrease priority"``.
   * - ``deleteentrylabel``
     - ``_(u'Remove item')``
     - Label associated with the "Remove from list" widget. i.e. ``"Remove this
       video"``.
   * - ``types``
     - ``() # All types``
     - List of selectable portal types to show in the selection
       panel. i.e. ``['Document']``
   * - ``typeview``
     - ``'file'``
     - Possible values are ``'file'``, ``'image'`` and ``'selection'``. Tuning
       on selection panel layout.
   * - ``imagetypes``
     - ``('Image', 'News Item')``
     - Sequence of portal types that can handle images (see `Todo`_)
   * - ``selectiontype``
     - ``'uid'``
     - Selected items are returned to the application (form) as UIDs. Other
       possible value is ``'url'``.
   * - ``showsearchbox``
     - ``True``
     - Do we show the searchbox?
   * - ``allowupload``
     - ``False``
     - Do we enable upload files through our widget if the user has appropriate
       permission? See `Uploadding in custom folderish type`_
   * - ``openuploadwidgetdefault``
     - ``False``
     - Do we display the upload widget by default?
   * - ``allowaddfolder``
     - ``False``
     - Do we enable adding new folders through our widget if the user has
       appropriate permission?
   * - ``allowimagesizeselection``
     - ``False``
     - If the image has multiple sizes, do we enable the selection of a
       particular size? (See the above note)
   * - ``forcecloseoninsert``
     - ``False``
     - Do we close the finder when an element is selected?
   * - ``base``
     - ``None``
     - The folderish object used as root of the finder when opening. ``None``
       means the Plone site. **Note that** by nature, this attribute cannot be
       set statically, in a ``FinderSelectWidget`` personal subclass for example
       as other can be. See the example in simple customizations on how to
       change the widget ``base`` attribute dynamically from the form class
       code.


Developer Howto
===============

How to use it in a WYSIWYG editor
---------------------------------

The more easy way is creating a specific view, because you will often need to
override the javascript method to select objects, and because each editor has
its specific negociations with the browser.

See ``collective.ckeditor`` package as example.


Uploadding in custom folderish type
-----------------------------------

If you want to let the plone finder users upload files in your custom or third
party folderish content types, you need to mark these types with the
``IFinderUploadCapable`` marker interface. As in this self-speaking ZCML
sample::

  <class class="my.content.folderish.MyFolderish">
    <implements
       interface="collective.plonefinder.browser.interfaces.IFinderUploadCapable" />
  </class>

Out of the box, ``collective.plonefinder`` enables upload in the Plone site
itself as well as in ``ATFolder`` and ``ATBTreeFolder``.

Todo
====

- Functional doctests

- i18n support

- Finder improvements:

  - Ajax opening/moving/resizing and all window effects inside the same browser
    window (in progress, need some js refactoring)

  - improve contextual actions menu (change workflow state, rename, delete,
    copy, paste ...)

  - add a finder menu action to show/hide the current selection list in right
    panel

  - remove items from selection list in finder window

- Improve zope3 reference widget properties

  - add option to hide/show or just mark selected items in finder browsing
    results (just need to store the finder blacklist in session)

  - add option to set a specific catalog query stored in session

  - add option to change finder catalog.

- New zope3 widget to store urls (for a string field)

- Archetypes support:

  - ATPloneFinderWidget for Reference fields (not a big challenge, just need to
    use ATReferenceBrowserWidget as base to start the work)

  - ATLinkWidget to store internal links

- Dexterity support (z3c.form)

- Supplement ``types`` and ``imagetypes`` attributes with others uning
  interfaces for a better flexibility.

- Provide as parameter a factory that provides the results in the desired
  format. i.e You need a particular attribute of the target or some computed
  value.

- Componentize the code for more flexibility.

Any contribution is welcome, contact support@ingeniweb.com.

Authors
=======

Jean-mat Grimaldi - Alter Way Solutions

Code repository
===============

https://github.com/collective/collective.plonefinder

Support
=======

- Questions and comments to support@ingeniweb.com
