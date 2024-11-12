library(xml2)


tmp <- tempfile()
download.file("https://www.penangmonthly.com/tag/statistics/rss", tmp)

content <- readLines(tmp)
unlink(tmp)
read_xml(content) |> 
    xml_find_all("./channel/item") |> 
    as_list() -> res

title <- sapply(res, \(x) x$title[[1]])
# date <- sapply(res, \(x) x$pubDate[[1]]) |> 
#     substr(start = 1, stop = 16) |>
#     as.Date(format = "%a, %d %b %Y")

date <- sapply(res, \(x) x[names(x) == "category"] |> 
    unlist() |> 
    grep(pattern = "[[:alpha:]]+\\s[[:digit:]]+", 
    value = TRUE) |> unname()) 
date <- paste("1", date) |> as.Date(format = "%d %B %Y")


path <- sapply(res, \(x) x$link[[1]])
image <- sapply(res, \(x) attributes(x$content)$url)
author <- sapply(res, \(x) x$creator[[1]])

data.frame(
    title = title, 
    date = format(date, "%Y-%m-01"), 
    path = path, image = image, author = author
) |> yaml::write_yaml("penang-monthly-stats.yaml", column.major = FALSE)
