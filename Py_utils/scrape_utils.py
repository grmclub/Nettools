# -*- coding: utf-8 -*-
import pycurl
import sys
import time
try :
    # Python 2
    from StringIO import StringIO
except ImportError :
    # Python 3
    from io import StringIO

class file_scraper:
    def __init__(self, proxyhost, proxyport, user="", passw=""):
        #conn params
        self.proxyhost = proxyhost.strip()
        self.proxyport = int(proxyport)
        self.user      = user
        self.passw     = passw
        self.agent     = "NIX download agent/1.0"

    def _create_obj(self):
       curl = pycurl.Curl()
       curl.setopt(pycurl.CONNECTTIMEOUT, 30)
       curl.setopt(pycurl.FOLLOWLOCATION, 1)
       curl.setopt(pycurl.MAXREDIRS, 5)
       curl.setopt(pycurl.NOSIGNAL, 1)
       curl.setopt(pycurl.PROXYPORT, self.proxyport)
       curl.setopt(pycurl.PROXY, self.proxyhost)
       curl.setopt(pycurl.TIMEOUT, 300)
       curl.setopt(pycurl.USERAGENT, self.agent)
       curl.setopt(pycurl.VERBOSE, 1)
       return curl

    def http_download_data(self, remote_url, filename, output_dir, postdata=""):
        with open(output_dir + filename, 'wb') as infile:
            curl = self._create_obj()
            curl.setopt(pycurl.URL, remote_url)
            curl.setopt(pycurl.WRITEDATA, infile)
            if postdata:
                curl.setopt(pycurl.POST, 1)
                curl.setopt(pycurl.POSTFIELDS, postdata)
            curl.perform()
            http_code = curl.getinfo(pycurl.HTTP_CODE)
            if (http_code < 200 and http_code > 250):
                curl.close()
                raise IOError("%s download file %s failed status code: %s" % (self.__class__.__name__,
                                                                              filename,
                                                                              http_code))
            curl.close()

    def https_download_data(self, remote_url, filename, output_dir):
        with open(output_dir + filename, 'wb') as infile:
            curl = self._create_obj()
            curl.setopt(pycurl.URL, remote_url)
            curl.setopt(pycurl.USERPWD, '%s:%s' % (self.user, self.passw))
            curl.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_BASIC)
            curl.setopt(pycurl.WRITEDATA, infile)
            curl.perform()
            http_code = curl.getinfo(pycurl.HTTP_CODE)
            if (http_code < 200 and http_code > 250):
                curl.close()
                raise IOError("%s download file %s failed status code: %s" % (self.__class__.__name__,
                                                                              filename,
                                                                              http_code))
            curl.close()

    def http_scrape_str(self, remote_url, postdata=""):
        curl = self._create_obj()
        buffer = StringIO()
        curl.setopt(pycurl.URL, remote_url)
        curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        if postdata:
            curl.setopt(pycurl.POST, 1)
            curl.setopt(pycurl.POSTFIELDS, postdata)
        curl.perform()
        http_code = curl.getinfo(pycurl.HTTP_CODE)
        if (http_code < 200 and http_code > 250):
            curl.close()
            raise IOError("%s download failed status code: %s\n %s" % (self.__class__.__name__,
                                                                       http_code,
                                                                       buffer.getvalue()))
        curl.close()
        return buffer.getvalue()

class unit_test:
    def __init__(self, host, port, user="", passw=""):
        self.scraper = file_scraper(host, port, user, passw)

    def test_http_download_data(self, url):
        self.scraper.http_download_data(url,"test_http.txt", "/tmp/")

    def test_https_download_data(self, url, user, passw):
        self.scraper.https_download_data(url,"test_https.txt", "/tmp/")

    def test_http_scrape_str(self, url):
        buf = self.scraper.http_scrape_str(url)
        print buf

    """
    add:
        1. grab filename from headers & override default filename
        2. variable settings for curl timeouts. Default settings assume worst pessimistic outcome.
        3. add sftp functionality
    """

def main():
    try:
        host  = "http://proxy.abc"
        port  = "8080"
        user  = "jjcale"
        passw = "xxx"
        test  = unit_test(host, port, user, passw)

        ##Test-1
        url = "http://abc"
        test.test_http_download_data(url)

        ##Test-2
        url = "https://bulkweb.nikkei.co.jp/cgi-bin/list.cgi"
        test.test_https_download_data(url, user, passw)

        ##Test-3
        url = "http://bcd"
        test.test_http_scrape_str(url)

    except Exception, err:
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()

if __name__ == "__main__":
    main()
