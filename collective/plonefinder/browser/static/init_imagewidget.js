if (! ("elmapps" in window)) {
    elmapps = {};
} 

initializeImageWidget = function(finder_url, initial_image_url, widget_id, input_id) {
    var node = document.querySelector('#'+widget_id);
    var parent = node.parentNode;
    parent.removeChild(node);
    elmapps[widget_id] = Elm.ImageWidget.init(
        {node: parent,
        // portal_url is global variable set by Plone
        flags: {widgetId: widget_id, inputId:input_id, relativeUrl: initial_image_url, portalUrl: portal_url}});
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

// finderSelectItem is called by plone_finder window when selecting an item
finderSelectItem = function(selector, title, image_preview, widget_id) {
    image_preview = (typeof image_preview != "undefined") ? image_preview : false;
    if (image_preview) selector = selector + '/@@images/image/preview' ;
    elmapps[widget_id].ports.relativeUrlPort.send(selector);
};

