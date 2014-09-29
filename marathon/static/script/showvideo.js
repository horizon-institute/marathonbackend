$(function() {
    
    function showItem(item) {
        var $this = $(item);
        $this.siblings().removeClass("fullwidth-item");
        var w = $("#bottom-content-wrapper").width() - 14;
        if ($this.hasClass("fullwidth-item")) {
            var v = $this.find("video");
            if (v.length) {
                v[0].pause();
            }
            $this.removeClass("fullwidth-item").css("width",w).animate({
                "width": "225px"
            }, {
                duration: 500,
                complete: function() {
                    $this.css("width","");
                }
            });
        } else {
            $this.animate({
                "width": w
            }, {
                duration: 500,
                complete: function() {
                    $this.addClass("fullwidth-item").css("width","");
                    if (!$this.find("video").length && !!+$this.attr("data-video-online")) {
                        $this.find(".item-video").append(
                            '<video src="'
                            + $this.attr("data-video-url")
                            + '" controls></video>'
                        );
                    }
                    
                    $("body").animate({
                        scrollTop: $this.offset().top
                    }, 500);
                }
            });
        }
    }
    
    $(".item").dblclick(function() {
        showItem(this);
    });
    $(".item-video img").click(function() {
        showItem(this.parentNode.parentNode);
    });
});
