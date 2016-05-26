使用火车头采集器（v7及以上版本均可）抓取Top250图书的基本信息以及短评内容的步骤：
1、使用规则Book_url.ljobx，初始网址为https://book.douban.com/top250?start=0，得到豆瓣排名前250的图书的书名和图书主页，图书主页的网址放到Book_url.txt中；
2、使用规则Book_inf.ljobx，初始网址为Book_url.txt中的网址，即图书主页的网址，从每一本书的主页上抓取图书的书名、作者和短评网址，由于抓取到的短评网址只是第一页的网址，所以将其扩充成前十页的短评网址，将扩充之后的所有短评网址放到Book_reviews.txt中；
3、使用规则Book_reviews.ljobx，初始网址为Book_reviews.txt中的网址，即图书短评信息的网址，从短评页面上抓取评论内容。
