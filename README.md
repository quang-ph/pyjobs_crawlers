# Jobs.pymi.vn Crawlers

[![Build Status](https://travis-ci.org/pymivn/pyjobs_crawlers.svg?branch=master)](https://travis-ci.org/pymivn/pyjobs_crawlers)

Run all spiders by

```
./runner
```

Or run single spider

```
./runner careerbuilder
```

##Hướng dẫn chạy spider thu thập dữ liệu công ty từ Vietnamworks

Cài đặt môi trường
```
pip install -r requirements.txt
```

Export đường dẫn tới thư mục driver (trong vnw/driver)
```
export PATH="/path/to/driver/folder:$PATH"
```

Di chuyển vào thư mục crawler
```
cd vnw
```

Khởi chạy spider
```
python run.py crawl vnw-company
```


## Test / lint

Để test style/lint chạy:

```
make lint
```

Chú ý, máy bạn cần cài sẵn `make`.

Để test các spider, chạy:

```
make test
```

## Đóng góp

- Tìm hiểu về [Scrapy](https://scrapy.org/)
- Fork project về tài khoản GitHub của bạn: https://github.com/pymivn/pyjobs_crawlers#fork-destination-box (bấm nút Fork góc trên bên phải).
- Chỉnh sửa các spiders trong spiders/ hoặc thêm spider mới
- Commit, push rồi tạo Pull Request https://github.com/pymivn/pyjobs_crawlers/compare

## Các tiêu chí về spider
- Mỗi job phải có tối thiểu 5 thông tin:
  ```
  ['name', 'province', 'url', 'work', 'specialize']
  ```
- Code chuẩn Pep8, độ dài mỗi dòng giới hạn là 100 ký tự.
- Python 2 (project được tạo trước khi Scrapy hỗ trợ Python3)

## Spiders
- Xem các spider trong https://github.com/pymivn/pyjobs_crawlers/tree/master/vnw/vnw/spiders
- TODO: fix Vietnamwork crawler
- TopCV: bỏ, quá ít job.

## Cài đặT

### python-dev, libffi-dev

Chạy lệnh sau để cài trên Ubuntu (các hệ điều hành khác sẽ có gói tương tự).

```
sudo apt-get install -y python-dev libffi-dev
```

để khỏi gặp lỗi


```
    c/_cffi_backend.c:2:20: fatal error: Python.h: No such file or directory
```

### libssl-dev

```
sudo apt-get install -y libssl-dev
```

để khỏi gặp lỗi

```
    build/temp.linux-x86_64-2.7/_openssl.c:423:25: fatal error: openssl/aes.h: No such file or directory
    compilation terminated.
    error: command 'x86_64-linux-gnu-gcc' failed with exit status 1
```

# TODO
- Thêm status của các crawler vào web
