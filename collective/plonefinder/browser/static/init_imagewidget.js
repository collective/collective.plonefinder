if (! ("elmapps" in window)) {
    elmapps = {};
} 

initializeImageWidget = function(finder_url, initial_image_url, field_htmlid) {
    var node = document.querySelector('#'+field_htmlid+' .imagewidget');
    elmapps[field_htmlid] = Elm.ImageWidget.embed(node, [field_htmlid, initial_image_url]);
    elmapps[field_htmlid].ports.remove.subscribe(function(field_htmlid) {
        storeImageUrl(field_htmlid, '');
    });

    elmapps[field_htmlid].ports.openfinder.subscribe(function(field_htmlid) {
        openFinder(finder_url);
    });
}

finderSelectItem = function(selector, title, image_preview, field_htmlid) {
    image_preview = (typeof image_preview != "undefined") ? image_preview : false;
    if (image_preview) selector = selector + '/@@images/image/preview' ;
    storeImageUrl(field_htmlid, selector);
}

storeImageUrl = function(field_htmlid, selector) {
    if (selector === '') {
      var image_url = '';
    } else {
      var image_url = portal_url + '/resolveuid/' + selector;
    }
    jQuery('#'+field_htmlid+' input').val(image_url);
    elmapps[field_htmlid].ports.url.send(image_url);
}

openFinder = function(url) {
    var finder_window = window.open(url,"plone_finder","menubar=no, status=no, scrollbars=no, menubar=no, width=980, height=650, left=20, top=20");
    finder_window.focus();
}
