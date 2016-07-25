if (! ("elmapps" in window)) {
    elmapps = {};
} 

initializeImageWidget = function(finder_url, initial_image_url, widget_id, input_id) {
    var node = document.querySelector('#'+widget_id);
    var parent = node.parentNode;
    elmapps[widget_id] = Elm.ImageWidget.embed(parent, [widget_id, input_id, initial_image_url]);    parent.removeChild(node);
    elmapps[widget_id].ports.openfinder.subscribe(function(widget_id) {
        // widget_id is unused
        // it is baked in finder_url
        openFinder(finder_url);
    });
};

openFinder = function(url) {
    var finder_window = window.open(url,"plone_finder","menubar=no, status=no, scrollbars=no, menubar=no, width=980, height=650, left=20, top=20");
    finder_window.focus();
};

finderSelectItem = function(selector, title, image_preview, widget_id) {
    image_preview = (typeof image_preview != "undefined") ? image_preview : false;
    if (image_preview) selector = selector + '/@@images/image/preview' ;
    // selector is the relative path from the portal
    // compute absolute_url to be stored
    var image_url = portal_url + '/resolveuid/' + selector;
    elmapps[widget_id].ports.url.send(image_url);
};

