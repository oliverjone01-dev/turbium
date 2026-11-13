from pathlib import Path
import re,shutil,zipfile,json
root=Path(__file__).resolve().parents[1];theme=root/'wordpress/dekoriya-atelier';theme.mkdir(parents=True,exist_ok=True)
for path in ['assets','media']:
 target=theme/path
 if target.exists():shutil.rmtree(target)
 if path=='media':shutil.copytree(root/path,target)
 else:
  target.mkdir(parents=True,exist_ok=True)
  sources=[root/n for n in ['index.html','site.css','wow.css','spatial.css','media.json','design-system.html','motion-map.html']]
  sources+=list((root/'media').glob('*.html'))
  refs=set()
  for source in sources:
   refs.update(re.findall(r'assets/[A-Za-z0-9_./-]+\.(?:webp|svg|jpg|jpeg|png|woff2?|ttf)',source.read_text()))
  for relative in refs:
   origin=root/relative
   if not origin.is_file():raise FileNotFoundError(relative)
   destination=theme/relative;destination.parent.mkdir(parents=True,exist_ok=True)
   shutil.copyfile(origin,destination)
for name in ['index.html','site.css','wow.css','spatial.css','motion-config.js','motion.js','app.js','media.json','motion-map.html','design-system.html']:
 if(root/name).exists():shutil.copyfile(root/name,theme/name)
(theme/'template-parts').mkdir(exist_ok=True)
s=(root/'index.html').read_text();body=re.search(r'<body>(.*)</body>',s,re.S).group(1);body=re.sub(r'<script src="(?:motion-config|motion|app)\.js(?:\?[^\"]*)?"[^>]*></script>','',body)
for i,line in enumerate(['Оформляем','пространства','для бизнеса.'],1):body=body.replace('<span>'+line+'</span>','<span>{{HERO_LINE_'+str(i)+'}}</span>',1)
(theme/'template-parts/landing.html').write_text(body)
(theme/'style.css').write_text('''/*
Theme Name: DEKORIYA Atelier Motion
Theme URI: https://github.com/oliverjone01-dev/turbium/tree/main/Decoriya/website
Author: DEKORIYA
Description: Многослойный hero, редактируемый оффер, галереи и адаптивная анимация без внешних JS-библиотек.
Version: 6.7.0
Requires at least: 6.6
Requires PHP: 8.0
Text Domain: dekoriya-atelier
License: GNU General Public License v2 or later
*/
''')
(theme/'functions.php').write_text('''<?php
if (!defined('ABSPATH')) { exit; }
add_action('after_setup_theme', function () {
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('html5', array('search-form', 'comment-form', 'gallery', 'caption', 'style', 'script'));
});
add_action('wp_enqueue_scripts', function () {
    $uri = get_template_directory_uri();
    $version = wp_get_theme()->get('Version') . '.' . max(filemtime(get_template_directory() . '/site.css'), filemtime(get_template_directory() . '/wow.css'), filemtime(get_template_directory() . '/spatial.css'), filemtime(get_template_directory() . '/app.js'), filemtime(get_template_directory() . '/motion.js'));
    wp_enqueue_style('dekoriya-base', $uri . '/site.css', array(), $version);
    wp_enqueue_style('dekoriya-wow', $uri . '/wow.css', array('dekoriya-base'), $version);
    wp_enqueue_style('dekoriya-spatial', $uri . '/spatial.css', array('dekoriya-wow'), $version);
    wp_enqueue_script('dekoriya-motion-config', $uri . '/motion-config.js', array(), $version, array('in_footer' => true, 'strategy' => 'defer'));
    wp_enqueue_script('dekoriya-motion', $uri . '/motion.js', array('dekoriya-motion-config'), $version, array('in_footer' => true, 'strategy' => 'defer'));
    wp_enqueue_script('dekoriya-app', $uri . '/app.js', array('dekoriya-motion'), $version, array('in_footer' => true, 'strategy' => 'defer'));
});
add_action('customize_register', function ($customizer) {
    $customizer->add_section('dekoriya_main', array('title' => 'Декория: главная', 'priority' => 30));
    $customizer->add_setting('dekoriya_headline', array('default' => "Оформляем\\nпространства\\nдля бизнеса.", 'sanitize_callback' => 'sanitize_textarea_field'));
    $customizer->add_control('dekoriya_headline', array('section' => 'dekoriya_main', 'label' => 'Заголовок hero (три строки)', 'type' => 'textarea'));
    $customizer->add_setting('dekoriya_contact_url', array('default' => 'https://profi.ru/profile/SerdyukovaAI/', 'sanitize_callback' => 'esc_url_raw'));
    $customizer->add_control('dekoriya_contact_url', array('section' => 'dekoriya_main', 'label' => 'Ссылка для обращения', 'type' => 'url'));
});
add_filter('pre_get_document_title', function ($title) {
    return is_front_page() ? 'Декория / оформление пространств для бизнеса' : $title;
});
add_action('wp_head', function () {
    if (!is_front_page()) { return; }
    $description = 'Флористика и декор для бизнеса в Москве и области. Олеся Овакимян и команда Декории. Концепция, подбор материалов и монтаж.';
    echo '<meta name="description" content="' . esc_attr($description) . '">';
    echo '<meta property="og:title" content="Декория / оформление пространств для бизнеса">';
    echo '<meta property="og:description" content="' . esc_attr($description) . '">';
    echo '<meta property="og:type" content="website">';
    echo '<meta property="og:image:width" content="1200">';
    echo '<meta property="og:image:height" content="900">';
    echo '<meta property="og:url" content="' . esc_url(home_url('/')) . '">';
    echo '<meta property="og:image" content="' . esc_url(get_template_directory_uri() . '/screenshot.png') . '">';
});
add_action('template_redirect', function () {
    if (!isset($_GET['dk_media'])) { return; }
    if (!is_string($_GET['dk_media'])) { wp_die('Фотография не найдена.', 'Декория', array('response' => 404)); }
    $id = sanitize_key(wp_unslash($_GET['dk_media']));
    $items = json_decode(file_get_contents(get_template_directory() . '/media.json'), true);
    $allowed = array_column($items, 'id');
    if (!in_array($id, $allowed, true)) {
        wp_die('Фотография не найдена.', 'Декория', array('response' => 404));
    }
    $document = file_get_contents(get_template_directory() . '/media/' . $id . '.html');
    $base = trailingslashit(get_template_directory_uri());
    $document = str_replace('../assets/', esc_url($base . 'assets/'), $document);
    $document = str_replace('../site.css', esc_url($base . 'site.css') . '?v=6.7.0', $document);
    $document = str_replace('../index.html', esc_url(home_url('/')), $document);
    status_header(200);
    header('Content-Type: text/html; charset=UTF-8');
    echo $document;
    exit;
});
function dekoriya_render_landing() {
    $path = get_template_directory() . '/template-parts/landing.html';
    if (!is_readable($path)) { return '<p>Не найден шаблон главной.</p>'; }
    $markup = file_get_contents($path);
    $base = trailingslashit(get_template_directory_uri());
    $markup = str_replace('assets/', esc_url($base . 'assets/'), $markup);
    $items = json_decode(file_get_contents(get_template_directory() . '/media.json'), true);
    foreach ($items as $item) {
        $route = add_query_arg('dk_media', $item['id'], home_url('/'));
        $markup = str_replace('href="media/' . $item['id'] . '.html"', 'href="' . esc_url($route) . '"', $markup);
    }
    foreach (array('motion-map.html', 'design-system.html') as $doc) {
        $markup = str_replace('href="' . $doc . '"', 'href="' . esc_url($base . $doc) . '"', $markup);
    }
    $contact = get_theme_mod('dekoriya_contact_url', 'https://profi.ru/profile/SerdyukovaAI/');
    $markup = str_replace('https://profi.ru/profile/SerdyukovaAI/', esc_url($contact), $markup);
    $headline = get_theme_mod('dekoriya_headline', "Оформляем\\nпространства\\nдля бизнеса.");
    $lines = explode("\\n", $headline);
    for ($i = 1; $i <= 3; $i++) {
        $markup = str_replace('{{HERO_LINE_' . $i . '}}', esc_html(isset($lines[$i - 1]) ? $lines[$i - 1] : ''), $markup);
    }
    return $markup;
}
''')
(theme/'header.php').write_text('''<?php if (!defined('ABSPATH')) { exit; } ?>
<!doctype html><html <?php language_attributes(); ?> data-asset-base="<?php echo esc_url(trailingslashit(get_template_directory_uri())); ?>"><head><meta charset="<?php bloginfo('charset'); ?>"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><link rel="icon" href="<?php echo esc_url(get_template_directory_uri() . '/assets/logo.svg'); ?>"><?php wp_head(); ?></head><body <?php body_class(); ?>><?php wp_body_open(); ?>
''')
(theme/'footer.php').write_text('<?php if (!defined(\'ABSPATH\')) { exit; } wp_footer(); ?></body></html>')
(theme/'front-page.php').write_text("<?php if (!defined('ABSPATH')) { exit; } get_header(); echo dekoriya_render_landing(); get_footer();")
(theme/'index.php').write_text("<?php if (!defined('ABSPATH')) { exit; } get_header(); if (is_home() || is_front_page()) { echo dekoriya_render_landing(); } else { echo '<main class=\"wrap section project-fallback\">'; while (have_posts()) { the_post(); the_title('<h1>', '</h1>'); the_content(); } echo '</main>'; } get_footer();")
# Export foundations for WordPress editor use without altering the frontend runtime.
palette={'burgundy':'#57212F','ivory':'#F6F0E5','ink':'#281C20','muted':'#6D5A60','rose':'#E8D9D3'}
theme_json={'version':3,'settings':{'color':{'palette':[{'slug':k,'name':k,'color':v}for k,v in palette.items()]},'layout':{'contentSize':'1312px'},'typography':{'fontFamilies':[{'slug':'golos','name':'Golos Text','fontFamily':'Golos, Arial, sans-serif'}]}}};(theme/'theme.json').write_text(json.dumps(theme_json,indent=2))
if (root/'qa/hero-desktop-v67.png').exists():shutil.copyfile(root/'qa/hero-desktop-v67.png',theme/'screenshot.png')
zip_path=root/'wordpress/dekoriya-atelier-v67.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for f in theme.rglob('*'):
  if f.is_file():z.write(f,str(f.relative_to(theme.parent)))
print(str(zip_path));print('MB',round(zip_path.stat().st_size/1024/1024,1))
