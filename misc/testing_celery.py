import streaming.streaming as stream
from time import sleep
keywords = ['john elton', 'sayonara,japan', '#milennials', 'internet sensation', 'buzz', 'nintendo switch black friday', 'the best']
for i in range(10):
	a = stream.start_stream.delay(keywords[i % 7])
	print(a.get())
	sleep(3)

# c = stream.stop_stream.delay(a.id)
# print(c.get())
# sleep(5)
# d = stream.stop_stream.delay(b.id)
# print(d.get())
