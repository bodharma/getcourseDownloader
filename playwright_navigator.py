from playwright.sync_api import sync_playwright


class Site:
    def __init__(self, base_url, playwright):
        self.base_url = base_url
        self.chromium = playwright.chromium.launch(headless=False, channel="chrome")
        self.context = self.chromium.new_context(record_har_path="atmarama.har",
                                                     record_har_url_filter="https://player02.getcourse.ru/**")


    def __exit__(self, exc_type, exc_val, exc_tb):
        self.context.close()
        self.chromium.close()

    def setup_page(self):
        page = self.context.new_page()
        return page

    def visit_page(self, page, url):
        page.goto(url, wait_until='domcontentloaded')
        page.wait_for_timeout(5000)

    def login(self, email, password):
        email = page.query_selector('input[name="email"]')
        password = page.query_selector('input[name="password"]')
        login_button = page.query_selector('#xdget441936_1_1_1_1_1_1_1_1_1_1')
        page.wait_for_timeout(1000)
        email.fill(email)
        password.fill(password)
        login_button.click()
        page.wait_for_timeout(5000)

    def verify_im_logged(self, page):
        title = page.query_selector('h1')
        assert title.inner_text() == 'Список тренингов'

    def go_over_iframes(self, page):
        iframes_list = page.query_selector_all('iframe')
        if not iframes_list:
            return
        for counter, iframe in enumerate(iframes_list):
            counter += 1
            iframe.scroll_into_view_if_needed()
            iframe.click()
            page.wait_for_timeout(10000)
            iframe.click()

    def get_weeks(self, page):
        all_links = page.query_selector_all('a')
        week_courses = {}
        for link in all_links:
            if link.inner_text():
                if 'НЕДЕЛЯ' in link.inner_text() or 'Комплекс' in link.inner_text():
                    week_courses[link.inner_text()] = {
                        "url": f"{self.base_url}{link.get_attribute('href')}",
                        "days": {}
                    }
        return week_courses

    def get_days(self, page):
        day_courses = {day.inner_text(): {"url": f"{self.base_url}{day.get_attribute('href')}"} for day in
                       page.query_selector_all('.link, .title') if day.inner_text()}
        return day_courses

    def get_practice_complexes(self, page):
        all_complexes_links = {complex.inner_text().replace("\n", " "): {"url": f"{self.base_url}{complex.get_attribute('href')}"}
                               for
                               complex in page.query_selector_all('.row a') if complex.inner_text()}
        return all_complexes_links

    def find_videos(self, lessons_data):
        for lesson in lessons_data['raw_lessons_links']:
            lesson_name, url = list(lesson.items())[-1]
            try:
                self.visit_page(page, url)
                self.context.tracing.start(snapshots=True)
                self.go_over_iframes(page)
                self.context.tracing.stop(path=f'{lesson_name}.zip')
                page.wait_for_timeout(5000)
            except:
                print(f"Something went wrong with {lesson_name}")
                continue


if __name__ == '__main__':
    with sync_playwright() as playwright:
        atmarama = Site(base_url='https://my.atmarama.yoga', playwright=playwright)
        page = atmarama.setup_page()
        atmarama.visit_page(page, atmarama.base_url)
        atmarama.login(email='your_email', password='your_password')
        atmarama.verify_im_logged(page)
