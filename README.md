# Research Topics

Thư viện công bố về cơ học tính toán, Scientific ML và vật liệu.

Website: **https://NhanNguyenMinh.github.io/research_topics/**

## Nội dung và trải nghiệm

- Trang chủ nhóm bài đọc nền tảng và công bố gần đây theo 8 chủ đề.
- Tìm theo tiêu đề, tác giả, DOI; lọc năm và bài trong 12 tháng.
- Bài quan trọng do biên tập tuyển chọn, có lý do gợi ý đọc; không tự động suy ra từ số trích dẫn.
- Lưu bài để đọc sau bằng localStorage, chỉ trên trình duyệt hiện tại.
- Metadata và DOI có liên kết nguồn để đối chiếu. Đây là danh mục tuyển chọn, không bảo đảm bao phủ toàn bộ lĩnh vực.

## Chạy tại máy

Cần Python 3.10+ và Node.js 22+ để chạy kiểm tra JavaScript. Website không cần npm hoặc framework.

```powershell
python scripts/validate.py
python -m unittest discover -s tests
node --test tests/model.test.mjs
python scripts/build.py
python -m http.server 8765 --directory dist
```

Mở http://localhost:8765. Tránh mở trực tiếp `index.html` bằng `file://`, vì trang tải JSON bằng fetch.

## Cập nhật

GitHub Actions kiểm tra mỗi ngày khoảng **07:20 giờ Việt Nam** (00:20 UTC); lịch GitHub có thể trễ, và scheduled workflows có thể bị tắt khi repo công khai không hoạt động trong thời gian dài. Có thể chạy thủ công trong **Actions → Update topics and deploy Pages → Run workflow**.

Luồng công khai tìm theo các truy vấn chủ đề trong `data/queries.json`, dùng [OpenAlex API](https://help.openalex.org/api/), rồi kiểm tra lại DOI, loại công bố và ngày xuất bản qua [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/). Không đọc danh sách tác giả cá nhân. Có thể đặt `OPENALEX_API_KEY` trong Repository Actions Secrets nếu hạn mức không khóa không đủ; không đưa khóa vào mã nguồn. Lần chạy mặc định kiểm tra tối đa 24 DOI mới để giới hạn chi phí và số yêu cầu. Không tải toàn văn PDF hoặc vượt rào truy cập nguồn.

```powershell
python scripts/update.py
python scripts/validate.py
python scripts/build.py
```

Ngày hiển thị là ngày công bố sớm nhất có trong metadata Crossref, ưu tiên lấy cả ngày online và ngày in; nếu nguồn chỉ cho năm/tháng thì giữ độ chính xác đó. Bản ghi có ngày tương lai hoặc thiếu ngày không được tự thêm. Preprint được đánh dấu riêng. Trích dẫn và preprint/bản tạp chí với DOI khác nhau có thể vẫn là hai bản ghi; trùng DOI được loại bỏ.

Chủ đề được gán bằng từ khóa tiêu đề, nên có thể sai hoặc bỏ sót. Bài mới tự động chỉ mang nhãn phát hiện theo chủ đề, không được tự gắn “quan trọng”. Sửa `topics`, `featured` và `reason` trong `data/papers.json` sau khi đọc bài. Quy trình giữ lại các chỉnh sửa này cho DOI đã có. Thêm bài thủ công cần có DOI đã đối chiếu Crossref và nguồn kiểm chứng. Các bản đính chính/rút bài chưa được giám sát tự động; cần kiểm tra thông báo trên trang nhà xuất bản khi sử dụng công bố.

## Triển khai GitHub Pages

Repo Settings → Pages → Source: **GitHub Actions**. Workflow chạy kiểm tra, dựng `dist/`, rồi dùng các Actions Pages chính thức. Artifact chỉ chứa 4 file giao diện, 3 file dữ liệu công khai và `.nojekyll`. Khi nguồn tạm lỗi, bản ghi cũ được giữ lại, trạng thái được hiển thị trên trang và workflow báo lỗi sau khi triển khai dữ liệu còn dùng được.

`data/status.json` phân biệt thời điểm dữ liệu thay đổi với lần thử kiểm tra nguồn gần nhất. Không có backend, analytics hoặc đăng nhập.

## Cấu trúc

```text
web/                    Giao diện HTML/CSS/JavaScript
data/papers.json        Công bố, DOI, chủ đề, lý do tuyển chọn và nguồn
data/topics.json        Chủ đề và từ khóa phân loại
data/queries.json       Truy vấn khám phá công khai
data/status.json        Trạng thái cập nhật
scripts/                Cập nhật, kiểm tra và build bằng Python chuẩn
tests/                  Kiểm tra metadata và hành vi lọc
.github/workflows/      Kiểm tra PR, cập nhật theo lịch và triển khai
```

Không đưa file cấu hình cá nhân hoặc credentials vào repo. `.gitignore` loại các đầu vào cục bộ; bước build chỉ sao chép danh sách file công khai được cho phép.
