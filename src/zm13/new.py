import re
import requests
from PyPDF2 import PdfReader
import io # ioモジュールをインポート

def extract_text_from_pdf(pdf_source):
    """
    指定されたPDFソース（ファイルパスまたはURL）からテキストを抽出します。
    テキスト選択可能なPDFファイルでのみ機能します。
    """
    pdf_file = None
    try:
        if pdf_source.startswith(('http://', 'https://')):
            print(f"URLからPDFをダウンロード中: {pdf_source}")
            response = requests.get(pdf_source, stream=True)
            response.raise_for_status() # HTTPエラーが発生した場合に例外を発生させる
            # メモリ内のバイトストリームとしてPDFを読み込む
            pdf_file = io.BytesIO(response.content)
        else:
            # ローカルファイルパスとしてPDFを読み込む
            pdf_file = open(pdf_source, 'rb')

        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or "" # ページからテキストを抽出し、Noneの場合は空文字列を追加
        return text
    except requests.exceptions.RequestException as e:
        print(f"PDFのダウンロード中にエラーが発生しました: {e}")
        return None
    except Exception as e:
        print(f"PDFからのテキスト抽出中にエラーが発生しました: {e}")
        return None
    finally:
        if pdf_file and hasattr(pdf_file, 'close'):
            pdf_file.close() # ファイルが開かれている場合は閉じる

def find_doi_in_text(text):
    """
    与えられたテキストからDOIを検索します。
    複数のDOIが見つかる可能性があります。
    """
    # DOIの一般的な正規表現パターン
    # 例: 10.1000/abcd.12345
    # doi:10.1000/abcd.12345
    # https://doi.org/10.1000/abcd.12345
    doi_pattern = r'\b(10\.\d{4,}(?:\.\d+)*\/\S+[^,;\s])'
    dois = re.findall(doi_pattern, text, re.IGNORECASE)
    # 重複を排除し、ユニークなDOIのみを返す
    return list(set(dois))

def get_reference_from_doi(doi):
    """
    Crossref APIを使用してDOIからリファレンス情報を取得します。
    """
    url = f"https://api.crossref.org/works/{doi}"
    headers = {
        "Accept": "application/json",
        "User-Agent": "APA Reference Generator (mailto:your.email@example.com)" # 適切なメールアドレスに置き換えてください
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # HTTPエラーが発生した場合に例外を発生させる
        data = response.json()
        return data.get('message')
    except requests.exceptions.RequestException as e:
        print(f"Crossref APIからのリファレンス取得中にエラーが発生しました: {e}")
        return None

def format_apa_reference(bib_data):
    """
    取得した書誌データからAPAスタイルのリファレンス文字列をフォーマットします。
    これは一般的なジャーナル記事のフォーマットです。
    """
    if not bib_data:
        return "利用可能な書誌データがありません。"

    # 著者名のフォーマット
    authors = bib_data.get('author', [])
    author_names = []
    for author in authors:
        given = author.get('given', '')
        family = author.get('family', '')
        if given and family:
            # 姓, 名の頭文字. (例: Smith, J.)
            author_names.append(f"{family}, {given[0]}.")
        elif family:
            author_names.append(family)

    if len(author_names) > 7:
        # 7人以上の著者の場合、最初の6人と最後の著者を記載し、間に省略記号を挿入
        formatted_authors = ", ".join(author_names[:6]) + ", ... " + author_names[-1]
    elif len(author_names) > 1:
        # 2人以上の著者の場合、最後の著者の前に"&"を挿入
        formatted_authors = ", ".join(author_names[:-1]) + " & " + author_names[-1]
    elif author_names:
        formatted_authors = author_names[0]
    else:
        formatted_authors = "著者不明"

    # 発行年の取得
    issued = bib_data.get('issued', {}).get('date-parts', [[None]])[0][0]
    year = issued if issued else "n.d." # 年が不明な場合は"n.d." (no date)

    # タイトル
    title = bib_data.get('title', [''])[0]
    if not title:
        title = "タイトル不明"

    # ジャーナル名
    container_title = bib_data.get('container-title', [''])[0]
    if not container_title:
        container_title = "ジャーナル名不明"

    # 巻、号、ページ
    volume = bib_data.get('volume', '')
    issue = bib_data.get('issue', '')
    page = bib_data.get('page', '')

    # DOI
    doi = bib_data.get('DOI', '')
    doi_url = f"https://doi.org/{doi}" if doi else ""

    # APAスタイルのフォーマット
    # 著者. (年). タイトル. ジャーナル名, 巻(号), ページ. DOI
    reference = f"{formatted_authors}. ({year}). {title}. *{container_title}*"
    if volume:
        reference += f", {volume}"
    if issue:
        reference += f"({issue})"
    if page:
        reference += f", {page}."
    else:
        reference += "." # ページがなくてもピリオドで閉じる

    if doi_url:
        reference += f" {doi_url}"

    return reference

def generate_apa_reference_from_pdf(pdf_source):
    """
    PDFソース（ファイルパスまたはURL）からDOIを抽出し、APAスタイルのリファレンスを生成します。
    """
    print(f"PDFソース '{pdf_source}' からテキストを抽出中...")
    text = extract_text_from_pdf(pdf_source)

    if not text:
        return "PDFからテキストを抽出できませんでした。ファイルがテキスト選択可能か、URLが正しいか確認してください。"

    print("テキストからDOIを検索中...")
    dois = find_doi_in_text(text)

    if not dois:
        return "PDFからDOIが見つかりませんでした。DOIが存在するか、正しい形式であるか確認してください。"

    references = []
    for doi in dois:
        print(f"DOI: {doi} のリファレンス情報を取得中...")
        bib_data = get_reference_from_doi(doi)
        if bib_data:
            apa_ref = format_apa_reference(bib_data)
            references.append(apa_ref)
        else:
            references.append(f"DOI: {doi} のリファレンス情報を取得できませんでした。")

    return "\n\n".join(references)

# 使用例
if __name__ == "__main__":
    # URLからのPDF読み込みテスト
    pdf_url = "https://link.springer.com/content/pdf/10.1186/s12651-021-00296-y.pdf"
    print("\n--- URLからのAPAスタイルリファレンス生成 ---")
    result_url = generate_apa_reference_from_pdf(pdf_url)
    print(result_url)
    print("--------------------------------------")

    # ローカルファイルからのPDF読み込みテスト (コメントアウトを外して使用してください)
    # pdf_local_path = "path/to/your/local_document.pdf" # <-- ここを実際のローカルPDFファイルのパスに置き換えてください
    # print("\n--- ローカルファイルからのAPAスタイルリファレンス生成 ---")
    # result_local = generate_apa_reference_from_pdf(pdf_local_path)
    # print(result_local)
    # print("--------------------------------------")
