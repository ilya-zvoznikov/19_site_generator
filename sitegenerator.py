from jinja2 import Environment, FileSystemLoader
import json
from livereload import Server
import os
import markdown

SITE_FOLDER = 'www'
ARTICLES_FOLDER = 'articles'


def load_config(json_filename):
    try:
        with open(json_filename, 'r', encoding='utf-8') as json_file_obj:
            return json.load(json_file_obj)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return


def create_index_page(jinja2_env, topics_list):
    index_template = jinja2_env.get_template('index.html')
    return index_template.render(topics=topics_list)


def create_topic_page(jinja2_env, topics_list, topic):
    topic_template = jinja2_env.get_template('topic.html')
    return topic_template.render(topics=topics_list, topic=topic)


def create_article_page(jinja2_env, topics_list, article, content):
    article_template = jinja2_env.get_template('article.html')
    return article_template.render(
        topics=topics_list,
        article=article,
        content=content,
    )


def convert_markdown_to_html(md_file_path):
    with open('articles/{}'.format(md_file_path), 'r', encoding='utf-8') as f:
        html_content = markdown.markdown(f.read())
    return html_content


def fix_text_bugs(html_content):
    return html_content.replace(':::', '>>>')


def create_link(md_filename):
    md_filename = md_filename.replace('.md', '.html')
    md_filename = md_filename.replace(' ', '_')
    md_filename = md_filename.replace('&', '').replace(';', '')
    return md_filename


def save_page(site_folder, page_path, content):
    fullpath = os.path.join(site_folder, page_path)
    subfolder, filename = os.path.split(fullpath)
    if not os.path.exists(subfolder):
        os.makedirs(subfolder)
    with open(fullpath, 'w', encoding='utf-8') as file_obj:
        file_obj.write(content)


def make_site():
    env = Environment(loader=FileSystemLoader('templates'))
    config_dict = load_config('config.json')
    topics_list = create_topics_list(config_dict)

    index = create_index_page(env, topics_list)
    save_page(SITE_FOLDER, 'index.html', index)

    for topic in topics_list:
        topic_page = create_topic_page(env, topics_list, topic)

        save_page(SITE_FOLDER, topic['link'], topic_page)

        for article in topic['articles']:
            html_content = convert_markdown_to_html(article['source'])
            html_content = fix_text_bugs(html_content)
            article_page = create_article_page(
                jinja2_env=env,
                topics_list=topics_list,
                article=article,
                content=html_content,
            )
            save_page(SITE_FOLDER, article['link'], article_page)


def create_topics_list(config_dict):
    topics_list = config_dict['topics']
    for topic in topics_list:
        topic['articles'] = []
        for article in config_dict['articles']:
            if article['topic'] == topic['slug']:
                topic['articles'].append(article)
        for article in topic['articles']:
            article['link'] = create_link(article['source'])
        topic_folder = os.path.split(topic['articles'][0]['link'])[0]
        topic['link'] = os.path.join(
            topic_folder,
            '{}.html'.format(topic_folder),
        )
    return topics_list


if __name__ == '__main__':
    make_site()
    server = Server()
    server.watch('templates/*.html', make_site)
    server.serve(root='www/')
