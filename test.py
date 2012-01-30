class FileManager:
  def HasFile(self, filename):
    return filename in self.files

  def GetFile(self, filename):
    return self.files[filename]




def main():
  ...


  assert fm.HasFile(opts.prefix + 'calendar/events/2012-01-02-foo.html')
  text = fm.GetFile(opts.prefix + 'calendar/events/2012-01-02-foo.html')
  dom = etree.parse(StringIO(text))
  assert dom.xpath('//title').text == 'Foo - Stanford Humanities Center'
  assert dom.xpath('//div[@id = "topnext"]')
  assert dom.xpath('//div[@id = "topnext"]')['href'] == 'calendar/events/2012-02.html'
  assert dom.xpath('//div[@id = "topnext"]').text == "Next"
