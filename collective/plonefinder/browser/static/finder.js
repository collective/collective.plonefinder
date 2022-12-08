/* Helpers
** =======
** $Id$
*/

var ua = navigator.userAgent;
var isIE8 = (ua.match(/MSIE 8\.0/));


var isIE = false;
var isOldIE = (isIE && ! isIE8)?true:false;

$.fn.changeClass = function(c1,c2) {
    return this.each(function() {
        this_class = $(this).attr('class');
        if (this_class){
          if (this_class.indexOf(c1) >= 0) {
              $(this).removeClass(c1);
              $(this).addClass(c2);
          }
        }
    });
};


$.fn.center = function() {
    return this.each(function() {
        var content = this;
        hh = window.innerHeight || document.documentElement.clientHeight;
        ww = window.innerWidth || document.documentElement.clientWidth;
        hscroll = document.documentElement.scrollTop || document.body.scrollTop;
        wscroll = document.documentElement.scrollLeft || document.body.scrollLeft;
        if (content.offsetHeight > hh)
            var top = 50;
        else
            var top = (hscroll + (hh / 2) - (content.offsetHeight / 2));
        $(content).css({
            top: top  + "px",
            left: (wscroll + (ww / 2) - (content.offsetWidth / 2)) + "px",
            position: 'absolute'
          });
          /* $(window).resize(function() {$(this).center();});*/
        });
}

$.fn.fullsize = function() {
    /* Give an element the full page dimension */
    return this.each (function() {
        var content = this;
        arrayPageSize = getPageSize();
        var w = arrayPageSize[0];
        var h = arrayPageSize[1];

        /* We need to find browser-corner-bottom position otherwhise xScroll and
           yScroll can't be found when browser is moved outside original page's
           frame */
        corner = document.getElementById('plone-browser-corner-resize');
        maxX = findPosX(corner);
        maxY = findPosY(corner);
        if (maxX > w) w = maxX + 30 ;
        if (maxY > h) h = maxY + 30 ;
        $(content).css({
            width:  w  + "px",
            height: h + "px"
        });
    });
}

$.fn.popup = function() {
    return this.each(function() {
        var popup = this;
        $('> .window', popup).center();
    });
}

String.prototype.capitalize = function() { //v1.0
    return this.replace(/\w+/g, function(a){
        return a.charAt(0).toUpperCase() + a.substr(1).toLowerCase();
    });
};

function findPosX(obj) {
    var curleft = 0;
    if (obj && obj.offsetParent) {
        while (obj.offsetParent) {
            curleft += obj.offsetLeft;
            obj = obj.offsetParent;
        }
    } else if (obj && obj.x) curleft += obj.x;
    return curleft;
}

function findPosY(obj) {
    var curtop = 0;
    if (obj && obj.offsetParent) {
        while (obj.offsetParent) {
            curtop += obj.offsetTop;
            obj = obj.offsetParent;
        }
    } else if (obj && obj.y) curtop += obj.y;
    return curtop;
}


function getPageSize(){

    var xScroll, yScroll;

    if (window.innerHeight && window.scrollMaxY) {
        yScroll = window.innerHeight + window.scrollMaxY;
        xScroll = window.innerWidth + window.scrollMaxX;
        var deff = document.documentElement;
        var wff = (deff&&deff.clientWidth) || document.body.clientWidth || window.innerWidth || self.innerWidth;
        var hff = (deff&&deff.clientHeight) || document.body.clientHeight || window.innerHeight || self.innerHeight;
        xScroll -= (window.innerWidth - wff);
        yScroll -= (window.innerHeight - hff);
    } else if (document.body.scrollHeight > document.body.offsetHeight || document.body.scrollWidth > document.body.offsetWidth){ // all but Explorer Mac
        xScroll = document.body.scrollWidth;
        yScroll = document.body.scrollHeight;
    } else { // Explorer Mac...would also work in Explorer 6 Strict, Mozilla and Safari
        xScroll = document.body.offsetWidth;
        yScroll = document.body.offsetHeight;
    }

    var windowWidth, windowHeight;
    if (self.innerHeight) { // all except Explorer
        windowWidth = self.innerWidth;
        windowHeight = self.innerHeight;
    } else if (document.documentElement && document.documentElement.clientHeight) { // Explorer 6 Strict Mode
        windowWidth = document.documentElement.clientWidth;
        windowHeight = document.documentElement.clientHeight;
    } else if (document.body) { // other Explorers
        windowWidth = document.body.clientWidth;
        windowHeight = document.body.clientHeight;
    }

    // for small pages with total height less then height of the viewport
    if(yScroll < windowHeight) {
        pageHeight = windowHeight;
    } else {
        pageHeight = yScroll;
    }

    // for small pages with total width less then width of the viewport
    if(xScroll < windowWidth) {
        pageWidth = windowWidth;
    } else {
        pageWidth = xScroll;
    }

    arrayPageSize = new Array(pageWidth, pageHeight, windowWidth, windowHeight);
    return arrayPageSize;
}

isInString = function(str1, str2) {
    try {
        var reg = new RegExp(".*" + str1 + ".*$", "i");
        if(str2.match(reg))
            return true;
        else
            return false;
    }
    catch(e) {return false}
}


function getBrowserData(formData, paramName) {
    var oRegex = new RegExp('[\?&]' + paramName + '=([^&]+)', 'i');
    var oMatch = oRegex.exec(formData);
    if (oMatch && oMatch.length > 1) return oMatch[1] ;
    else return '' ;
}

function getQueryObject(query) {
    var Params = new Object();
    var listDatas = new Object();
    var ParamsList = new Array();
    if (! query) return Params; // return empty object
    var Pairs = query.split(/[;&]/);
    for (var i = 0; i < Pairs.length; i++) {
        var KeyVal = Pairs[i].split('=');
        if (! KeyVal || KeyVal.length != 2) continue;
        var key = KeyVal[0];
        var kvalue = decodeURI(KeyVal[1]);
        if (isInString(':list', key)) {
            if (typeof listDatas[key] != 'undefined') {
                // trop nul le javascript
                toto = new Array(kvalue);
                listDatas[key] = listDatas[key].concat(toto);
            }
            else {
                listDatas[key] = new Array(kvalue);
            }
            var val = listDatas[key];
        }
        else {
            var val = kvalue;
        }
        Params[key] = val;
        keyznothere = true;
        $.each(ParamsList, function() {
            if (this==key) {
                keyznothere = false;
                return false;
            }
        });
        if (keyznothere) ParamsList[i] = key;
    }
    return new Array(Params, ParamsList);
}

compileData = function(dataname, data, formData) {

    if (formData) {
        if (!isInString(dataname, formData)) {
            formData = formData + '&' + dataname + '=' + encodeURI(data);
        }
        else if (data) {
            paramsObj = getQueryObject(formData);
            params = paramsObj[0];
            params[dataname]= encodeURI(data);
            paramsList = paramsObj[1];
            formData = '';
            for ( var i = 0; i < paramsList.length; i++ ) {
                value = params[paramsList[i]];
                if (typeof value == 'string'){
                    if (formData) {
                        formData = formData + '&';
                    }
                    formData = formData + paramsList[i] + '=' +  encodeURI(value);
                }
                else if (typeof value=='object') {
                    for ( var j = 0; j < value.length; j++ ) {
                        if (formData) {
                            formData = formData + '&';
                        }
                        formData = formData + paramsList[i] + '=' +  encodeURI(value[j]);
                    }
                }
            }
        }
        return formData;
    }
    return dataname + '=' + encodeURI(data);
}

// absolutize a block position
// used for contextual menus positioning
// width and height can be forced
absolutizeBlockPosition = function(block, width, height) {
    bwidth = (typeof width == "undefined") ? block.width() : width;
    bheight = (typeof height == "undefined") ? block.height() : height;
    offsetpos = block.offset();
    block.css('position', 'absolute');
    block.css('z-index', '5000');
    block.css(offsetpos);
    postop = offsetpos.top;
    posleft = offsetpos.left;
    wwidth = $(window).width();
    wheight = $(window).height();
    if (posleft+bwidth > wwidth) block.css({'left': wwidth-bwidth-5});
    if (postop+bheight > wheight) block.css({'top': wheight-bheight-5});
}

/*

  Browser main object

*/

var Browser = {
    maximized: false,
    url: null,
    field_name: null,
    reference_script: null,
    options: null,
    typeview: 'image',
    left: 0,
    top: 0,
    width: 450,
    height: 300,
    fixedHeight: 0,
    ispopup: false,
    formdata: '',
    finderUrl: '@@plone_finder',
    forcecloseoninsert: 0
};

Browser.fixHeight = function() {
    return Browser.fixedHeight || (Browser.fixedHeight = (
        $('#plone-browser-body')[0].offsetTop
            + parseInt($('#plone-browser-body').css('marginBottom'))
            + parseInt($('#plone-browser-body').css('marginTop'))
            + parseInt($('.statusBar', Browser.window).css('height'))
            + parseInt($('#plone-browser-body').css('borderTopWidth'))
            + parseInt($('#plone-browser-body').css('borderBottomWidth'))
            + 15
    ));
}

Browser.close = function() {
    if (Browser.ispopup) {
        top.window.close();
    }
    else {
        $('#plone-browser').remove();
        Browser.window = null;
        $(window).unbind('resize');
    }
}

Browser.maximize = function() {
    arrayPageSize = getPageSize();
    var screenWidth = arrayPageSize[2];
    var screenHeight = arrayPageSize[3];
    Browser.width = screenWidth - Browser.left - 10;
    Browser.height = screenHeight - Browser.top - 100;
    Browser.size({width: Browser.width, height: Browser.height});
    Browser.window.center();
};

Browser.size = function(top, left, width, height) {
    if (!arguments[0]) {
        var wnd = Browser.window.get(0);
        Browser.left = wnd.offsetLeft;
        Browser.top = wnd.offsetTop;
        Browser.width = wnd.offsetWidth;
        Browser.height = wnd.offsetHeight;
        return { left: Browser.left, top: Browser.top,
                 width: Browser.width, height: Browser.height };
    } else if (typeof arguments[0] == 'string')
        return Browser.window.get(0)['offset' + arguments[0].capitalize()];
    if (arguments.length == 4) {
        Browser.left = left; Browser.top = top;
        Browser.width = width; Browser.height = height;
    } else if (arguments.length == 1) {
        var size = arguments[0];
        for (attr in Browser.size())
            Browser[attr] = size[attr] != undefined ? size[attr] : Browser[attr];
    }
    /* Settle a minimal size */
    Browser.width = Browser.width < 380 ? 380 : Browser.width;
    Browser.height = Browser.height < 220 ? 220 : Browser.height;

    Browser.window
        .css({ top:Browser.top + 'px', left:Browser.left + 'px' })
        .width(Browser.width + 'px')
        .height(Browser.height + 'px');

    /* Compute browser-body-height, as it's the one which impact height */
    if (height || arguments[0]['height']) {
        var bodyHeight = Browser.height;
        bodyHeight -= Browser.fixHeight();
        bodyHeight -= 8;
        $('#plone-browser-body').height(bodyHeight + 'px');
    }
    $('#plone-browser .overlay').fullsize();
};

Browser.setView = function(typeview) {

    Browser.typeview = typeview;
    /* too slow for just changing style*/
    /* Browser.update('', Browser.formData); */

    if (typeview == 'file') {
        $('#plone-browser-body #sortheaders').css('display','block');
        $('#plone-browser-body .floatContainer')
            .changeClass('floatContainer','listContainer')
            .changeClass('portrait','portrait_icon')
            .changeClass('landscape','landscape_icon');
        $('#plone-browser-body img').each (function() {
            src = this.src;
            this.src = src.replace(/\/image_thumb/gi, '/image_listing');
            if ($.browser.msie) {
                oldstyle = $(this).attr('style');
                $(this).attr('style', oldstyle.replace(/px !important/gi, 'px'));
            }
        })
            }
    else {
        $('#plone-browser-body #sortheaders').css('display', 'none');
        $('#plone-browser-body .listContainer')
            .changeClass('listContainer', 'floatContainer')
            .changeClass('portrait_icon', 'portrait')
            .changeClass('landscape_icon', 'landscape');
        $('#plone-browser-body img').each (function() {
            src = this.src;
            this.src = src.replace(/\/image_listing/gi, '/image_thumb');
            if ($.browser.msie) {
                oldstyle = $(this).attr('style');
                $(this).attr('style', oldstyle.replace(/px/gi, 'px !important'));
            }
        });
    }

    $('#menuViews a').removeClass('selected');
    $('#menuViews a.' + typeview + 'View').addClass('selected');

};

Browser.open = function(browsedpath) {
    var aUrl = Browser.finderUrl;
    var data = {
        field_name: Browser.field_name,
        browsedpath: encodeURI(browsedpath),
        typeview: Browser.typeview
    };
    $('.statusBar > div', Browser.window).hide().filter('#msg-loading').show();
    $.post(aUrl, data, function(html) {
        Browser.close();
        $(document.body).append(html);
        $('#plone-browser').popup();
        Browser.window = $('#plone-browser > .window');
        $('#plone-browser-tab').mousedown(Browser.setMovable);
        $('#plone-browser-corner-resize').mousedown(Browser.setResizable);
        if (Browser.maximized)
            Browser.maximize();
        else
            Browser.size(Browser.top, Browser.left, Browser.width, Browser.height);
        $('.statusBar > div', Browser.window).hide().filter('#msg-loading').hide();
        TB_unlaunch();
        TB_launch();
        $(window).resize(function() {Browser.maximize();});
        Browser.batch();
    });
};

Browser.update = function(browsedpath, formData, b_start, sort_on, sort_order, nocompil) {
    $('.statusBar > div', Browser.window).hide().filter('#msg-loading').show();
    var aUrl = Browser.finderUrl;
    var size = Browser.size();
    var bodyHeight = $('#plone-browser-body')[0].offsetHeight;
    Browser.formData = $('#nextQuery').val();
    if (typeof formData == "undefined" || !formData) {
        formData = Browser.formData;
    }
    if (!nocompil) {
        formData = compileData('typeview', Browser.typeview, formData);
        if (typeof browsedpath != "undefined") formData = compileData('browsedpath', browsedpath, formData);
        if (typeof b_start != "undefined") formData = compileData('b_start:int', b_start, formData);
        if (typeof sort_on != "undefined") {
            formData = compileData('finder_sort_on', sort_on, formData);
            if ($('#previousSearch').length) {
                formData = compileData('SearchableText', $('#previousSearch').val(), formData);
                formData = compileData('searchsubmit:int', '1', formData);
            }
        }
        if (typeof sort_order != "undefined") formData = compileData('sort_order', sort_order, formData);
        formData = compileData('field_name', Browser.field_name, formData);
        formData = compileData('onlybody', 'true', formData);
    }
    $.ajax({
        type: 'GET',
        url: aUrl,
        data: formData,
        dataType: 'html',
        contentType: "text/html; charset=utf-8",
        success: function(html) {
            $('#browser-crumbs, #browser-columns, #plone-browser-menu, #plone-browser-navigation, .listingBar').remove();
            $('#start-refresh').after(html);
            /*if (Browser.maximized)
              Browser.maximize();
              else
              Browser.size(size);*/
            if (! isOldIE) {
                $('.finder_panel').height(bodyHeight - 12 + 'px');
            }
            else {
                $('.finder_panel').height(bodyHeight + 'px');
            }
            $('#plone-browser-body').css('visibility', 'visible');
            $('#plone-browser-navigation').css('visibility', 'visible');
            $('.statusBar > div', Browser.window).hide().filter('#msg-done').show();
            $('#msg-done').fadeOut(5000);
            TB_unlaunch();
            TB_launch();
            Browser.url = $('#browsed_url').val();
            Browser.batch();
            Browser.displayactionmenus();
        } });
}

Browser.openRightPanel = function() {
    rightpanel = $('#right-panel');
    rightpanel.empty();
    $(rightpanel.parent()).show();
}

Browser.closeRightPanel = function() {
    rightpanel = $('#right-panel');
    rightpanel.empty();
    $(rightpanel.parent()).hide();
    Browser.unselectActions ();
}

Browser.unselectActions = function() {
    $('#menuActions a').removeClass('selected');
}

Browser.openUploader = function() {
    var uploadButton = $('#menuActions .uploadView');
    var uploadContainer = $('#right-panel');
    if (! uploadButton.hasClass('selected')) {
        Browser.unselectActions ();
        var uploadUrl = Browser.url + '/@@finder_upload';
        Browser.openRightPanel();
        uploadButton.addClass('selected');
        $.ajax({
            type: 'GET',
            url: uploadUrl,
            data: '',
            dataType: 'html',
            contentType: "text/html; charset=utf-8",
            success: function(html) {
                uploadContainer.html(html);
            } });
    }
    else   {
        Browser.closeRightPanel();
        uploadContainer.empty();
        Browser.unselectActions ();
    }
}

Browser.onUploadComplete = function() {
    // remove upload form
    Browser.closeRightPanel();
    // update to the last batched page (TODO > update with the last page)
    var b_start = $('#start_after_upload').val();
    Browser.update('', '', b_start);
}

Browser.openAddFolderForm = function() {
    var addFolderButton = $('#menuActions .addFolderView');
    var addFolderContainer = $('#right-panel');
    if (! addFolderButton.hasClass('selected')) {
        Browser.unselectActions ();
        var addFolderUrl = Browser.url + '/@@finder_add_folder';
        Browser.openRightPanel();
        addFolderButton.addClass('selected');
        $.ajax({
            type: 'GET',
            url: addFolderUrl,
            data: '',
            dataType: 'html',
            contentType: "text/html; charset=utf-8",
            success: function(html) {
                addFolderContainer.html(html);
            } });
    }
    else   {
        Browser.closeRightPanel();
        addFolderContainer.empty();
        Browser.unselectActions ();
    }
}

Browser.createFolder = function() {
    $('.statusBar > div', Browser.window).hide().filter('#msg-loading').show();
    createFolderUrl = Browser.url + '/@@finder_create_folder';
    var folderForm = $('#create-new-folder');
    var formData = $('input:not([type=button]), textarea', folderForm).serialize();
    $.ajax({
        type: 'GET',
        url: createFolderUrl,
        data: formData,
        dataType: "text",
        contentType: "text/html; charset=utf-8",
        success: function(html) {
            Browser.update();
        } });
}

Browser.setResizable = function(e) {
    Browser.maximized = false;
    Browser.size();
    Browser.start_width = Browser.width;
    Browser.start_height = Browser.height;
    Browser.start_width -= e.clientX + document.documentElement.scrollLeft;
    Browser.start_height -= e.clientY + document.documentElement.scrollTop;
    document.body.style.cursor = 'se-resize';
    $(document.body).mousemove(Browser.resize).mouseup(Browser.drop);
    return false;
};

Browser.resize = function(e) {
    var x = e.clientX + document.documentElement.scrollLeft;
    var y = e.clientY + document.documentElement.scrollTop;
    var browserWidth = (Browser.start_width + x);
    var browserHeight = (Browser.start_height + y);
    browserHeight -= 10;
    Browser.size({ width: browserWidth, height:  browserHeight});
    return false;
};

Browser.setMovable = function(e) {
    var e = e || window.event;
    Browser.maximized = false;
    Browser.start_x = Browser.size().left;
    Browser.start_y = Browser.size().top;
    Browser.start_x -= e.clientX + document.documentElement.scrollLeft;
    Browser.start_y -= e.clientY + document.documentElement.scrollTop;
    $(document.body).mousemove(Browser.move).mouseup(Browser.drop);
    return false;
};

Browser.move = function(e) {
    var e = e || window.event;
    var x = e.clientX + document.documentElement.scrollLeft;
    var y = e.clientY + document.documentElement.scrollTop;
    Browser.size({left: (Browser.start_x + x), top: (Browser.start_y + y)});
    return false;
}


Browser.drop = function(e) {
    document.body.style.cursor = '';
    $(document.body)
        .unbind('mousemove', Browser.resize)
        .unbind('mousemove', Browser.move)
        .unbind('mouseup', Browser.drop);

    //.unmousemove(Browser.resize)
    //.unmousemove(Browser.move)
    //.unmouseup(Browser.drop);
};

Browser.search = function() {
    // var SearchableText = $('#SearchableText').val();
    var searchform = $('#finderSearchForm');
    Browser.formData = $('#nextQuery').val();
    var formData = $('input:not([type=submit]), textarea, select', searchform).serialize() + '&' + Browser.formData;
    var browsedpath = $('#browsedpath').val();
    Browser.update(browsedpath, formData);
};

Browser.sorton = function(sort_on, sort_order) {
    Browser.update('', '', 0, sort_on, sort_order);
}

/* redefine this method in your own widget see ckeditor finder as example or
   just create a finderSelectItem function in your window.opener  */

Browser.selectItem = function (UID, title, image_preview) {
    $('.statusBar > div', Browser.window).hide().filter('#msg-loading').show();
    var fieldid = getBrowserData(Browser.formData, 'fieldid');
    if (typeof window.opener.finderSelectItem !='undefined') window.opener.finderSelectItem(UID, title, image_preview, fieldid);
    else {
        if (typeof image_preview == "undefined" || !image_preview) alert("Selected: " + UID + " for fieldid " + fieldid);
        else alert("Selected a middle size image with this UID: " + UID + " for fieldid " + fieldid);
    }
    if (Browser.forcecloseoninsert) Browser.close();
    else {
        $('.statusBar > div', Browser.window).hide('10000').filter('#msg-done').show();
        $('#msg-done').fadeOut(10000);
    }
};


Browser.batch = function() {
    $('#plone-browser .listingBar a').click(
        function(){
            var batchUrl = this.href;
            var queryString = batchUrl.replace(/^[^\?]+\??/,'');
            Browser.update ('', queryString);
            this.blur();
            return false;
        }
    );
}

Browser.displayactionmenus = function() {
    $('a.actionMenusButton').click(function(){
        $(this).addClass('selected');
        rel = $(this).parent();
        menu = $('.finderActionMenuContainer', rel);
        if ($(this).parents('.floatContainer').length) {
            absolutizeBlockPosition($(rel),menu.width(),menu.height());
        }
        menu.show();
        menu.mouseleave(function(){
            rel = $(this).parent();
            $(rel).removeAttr('style');
            $('a.actionMenusButton', rel).removeClass('selected');
            $(this).hide();
        });
    });
}

Browser.batchresize = function() {
    var b_size = $('#b_size').val();
    formData = compileData('b_size:int', b_size, $('#b_size_query').val());
    Browser.update('', formData);
}

Browser.Popup_init = function() {
    $('body').css('overflow', 'hidden');
    Browser.window = $('#plone-browser > .window');
    arrayPageSize = getPageSize();
    if (! isOldIE) {
        $('.popup .finder_panel').height(arrayPageSize[3] -130);
    }
    else {
        $('.popup .finder_panel').height(arrayPageSize[3] - 115);
    }
    $('.popup #plone-browser-body').css('visibility','visible');
    $('.popup #plone-browser-navigation').css('visibility', 'visible');
    Browser.displayactionmenus();
    Browser.batch();

};

Browser.init = function() {
    Browser.typeview = $('#typeview').val();
    Browser.formData = $('#nextQuery').val();
    Browser.url = $('#browsed_url').val();
    Browser.finderUrl = '@@' + $('#finderName').val();
    Browser.forcecloseoninsert = parseInt($('#forcecloseoninsert').val()) ;
    if ($('#plone-browser.popup')) {
        Browser.ispopup =true;
        Browser.Popup_init();
        $(window).bind('resize', Browser.Popup_init);
    }
}

$(document).ready(function(){
    Browser.init();
})
