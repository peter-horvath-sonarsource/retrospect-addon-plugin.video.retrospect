# coding:Cp1252

import chn_class
from regexer import Regexer
from mediaitem import MediaItem


class Channel(chn_class.Channel):
    """
    main class from which all channels inherit
    """

    def __init__(self, channel_info):
        """ Initialisation of the class.

        All class variables should be instantiated here and this method should not
        be overridden by any derived classes.

        :param ChannelInfo channel_info: The channel info object to base this channel on.

        """

        chn_class.Channel.__init__(self, channel_info)

        # ============== Actual channel setup STARTS here and should be overwritten from derived classes ===============
        self.noImage = "vtmimage.jpg"

        # setup the urls
        self.mainListUri = "http://nieuws.vtm.be/herbekijk"
        self.baseUrl = "http://nieuws.vtm.be"

        # setup the main parsing data
        self.episodeItemRegex = '<li><a[^>]+href="/([^"]+)" class="level-1[^>]+>([^<]+)</a>'
        self._add_data_parser(self.mainListUri, creator=self.create_episode_item, parser=self.episodeItemRegex)

        video_item_regex = r'<article[^<]+has-video"[^>]*>\W*<a href="(?<Url>[^<"]+)"[^>]*>\W+' \
                           r'<div[^<]+<img[^>]+src="(?<Thumb>[^"]+)"[^>]*>[\w\W]{0,500}?<h3[^>]*>' \
                           r'(?:\W+<span[^>]*>[^>]*>)?(?<Title>[^<]+)</h3>\W+<div[^<]+<time[^>]+' \
                           r'datetime="(?<DateTime>[^"]+)"[^<]+</time>\W*</div>\W*<p[^>]+>*' \
                           r'(?<Description>[^<]+)'
        video_item_regex = Regexer.from_expresso(video_item_regex)
        self._add_data_parser("*", creator=self.create_video_item, parser=video_item_regex,
                              updater=self.update_video_item)

        stadion_regex = r'<article[^>]*>\W*<div class="image is-video">\W*<a href="(?<Url>[^"]+)' \
                        r'[^>]*>\W*<img[^>]+src="(?<Thumb>[^"]+)"[\w\W]{0,1000}?<h3 class=' \
                        r'"pagemanager-item-title">\W*<span>\W*<a[^>]*>(?<Title>[^<]+)[\w\W]' \
                        r'{0,1000}?<div class="teaser">\W*<a[^>]+>(?<Description>[^<]+)'
        stadion_regex = Regexer.from_expresso(stadion_regex)
        self._add_data_parser("http://nieuws.vtm.be/stadion",
                              parser=stadion_regex, creator=self.create_video_item,
                              updater=self.update_video_item)

        self.mediaUrlRegex = '<source[^>]+src="([^"]+)"[^>]+type="video/mp4"[^>]*/>'
        self.pageNavigationRegex = ''
        self.pageNavigationRegexIndex = 0

        #===============================================================================================================
        # non standard items

        #===============================================================================================================
        # Test cases:

        # ====================================== Actual channel setup STOPS here =======================================
        return

    def create_episode_item(self, result_set):
        """ Creates a new MediaItem for an episode.

        This method creates a new MediaItem from the Regular Expression or Json
        results <result_set>. The method should be implemented by derived classes
        and are specific to the channel.

        :param list[str]|dict[str,str] result_set: The result_set of the self.episodeItemRegex

        :return: A new MediaItem of type 'folder'.
        :rtype: MediaItem|none

        """

        # dummy class
        item = MediaItem(result_set[1], "%s/%s" % (self.baseUrl, result_set[0]))
        item.complete = True
        item.icon = self.icon
        item.thumb = self.noImage
        item.complete = True
        if "/het-weer" in item.url:
            item.type = "video"
            item.complete = False
        return item

    def create_video_item(self, result_set):
        """ Creates a MediaItem of type 'video' using the result_set from the regex.

        This method creates a new MediaItem from the Regular Expression or Json
        results <result_set>. The method should be implemented by derived classes
        and are specific to the channel.

        If the item is completely processed an no further data needs to be fetched
        the self.complete property should be set to True. If not set to True, the
        self.update_video_item method is called if the item is focussed or selected
        for playback.

        :param list[str]|dict result_set: The result_set of the self.episodeItemRegex

        :return: A new MediaItem of type 'video' or 'audio' (despite the method's name).
        :rtype: MediaItem|none

        """

        title = result_set["Title"]
        url = "%s%s" % (self.baseUrl, result_set["Url"])

        item = MediaItem(title, url)
        item.type = 'video'
        item.thumb = result_set["Thumb"]
        item.description = result_set.get("Description", None)
        item.complete = False

        if "DateTime" not in result_set:
            return item

        date_info = result_set["DateTime"]
        info = date_info.split("T")
        date_info = info[0]
        time_info = info[1]
        date_info = date_info.split("-")
        time_info = time_info.split(":")
        item.set_date(date_info[0], date_info[1], date_info[2], time_info[0], time_info[1], 0)
        return item
