.. contents::

   Ajax popup to reference plone contents.
   
   This code is an extraction of plonearticle explorer for referencables contents
   The intention is to make it usable for any content type in different situations :
   
   - for referencable fields with a special widget (collective.orderrefswidget which will come later)
   
   - for collective.ckeditor (in developpement) or any possible wysiwyg editor for referencing images or contents inside a rich text field,
     it's also possible to upload of files or images with this product (we use collective.uploadify)
   
   - for links fields (as remoteUrl in ATLink) to reference internal links   
      
   
   Don't use it in a production site for now (this product is under developpement just for a specific usecase)
   
   This work has been started by Christophe Bosse & Jean-mat Grimaldi in 2007.
   
   TODO :
   -----
   
   - some js refactoring
   
   - some css refactoring
   
   - any kind of refactoring
   
   - extended search form
   
   - 
   
   HOW TO USE IT  :
   ---------------
   
   See the collective.ckeditor product as example
   

.. Note!
   -----

  - Code repository: https://svn.plone.org/svn/collective/collective.plonefinder/trunk

  - Questions and comments to support@ingeniweb.com

