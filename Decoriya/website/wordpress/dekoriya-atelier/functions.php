<?php
if (!defined('ABSPATH')) { exit; }
add_action('after_setup_theme', function () {
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('html5', array('search-form', 'comment-form', 'gallery', 'caption', 'style', 'script'));
});
add_action('wp_enqueue_scripts', function () {
    $uri = get_template_directory_uri();
    $version = wp_get_theme()->get('Version') . '.' . max(filemtime(get_template_directory() . '/site.css'), filemtime(get_template_directory() . '/wow.css'), filemtime(get_template_directory() . '/app.js'), filemtime(get_template_directory() . '/motion.js'));
    wp_enqueue_style('dekoriya-base', $uri . '/site.css', array(), $version);
    wp_enqueue_style('dekoriya-wow', $uri . '/wow.css', array('dekoriya-base'), $version);
    wp_enqueue_script('dekoriya-motion-config', $uri . '/motion-config.js', array(), $version, array('in_footer' => true, 'strategy' => 'defer'));
    wp_enqueue_script('dekoriya-motion', $uri . '/motion.js', array('dekoriya-motion-config'), $version, array('in_footer' => true, 'strategy' => 'defer'));
    wp_enqueue_script('dekoriya-app', $uri . '/app.js', array('dekoriya-motion'), $version, array('in_footer' => true, 'strategy' => 'defer'));
});
add_action('customize_register', function ($customizer) {
    $customizer->add_section('dekoriya_main', array('title' => 'Декория: главная', 'priority' => 30));
    $customizer->add_setting('dekoriya_headline', array('default' => "Оформляем\nпространства\nдля бизнеса.", 'sanitize_callback' => 'sanitize_textarea_field'));
    $customizer->add_control('dekoriya_headline', array('section' => 'dekoriya_main', 'label' => 'Заголовок hero (три строки)', 'type' => 'textarea'));
    $customizer->add_setting('dekoriya_contact_url', array('default' => 'https://profi.ru/profile/SerdyukovaAI/', 'sanitize_callback' => 'esc_url_raw'));
    $customizer->add_control('dekoriya_contact_url', array('section' => 'dekoriya_main', 'label' => 'Ссылка для обращения', 'type' => 'url'));
});
function dekoriya_render_landing() {
    $path = get_template_directory() . '/template-parts/landing.html';
    if (!is_readable($path)) { return '<p>Не найден шаблон главной.</p>'; }
    $markup = file_get_contents($path);
    $base = trailingslashit(get_template_directory_uri());
    $markup = str_replace('assets/', esc_url($base . 'assets/'), $markup);
    $markup = str_replace('href="media/', 'href="' . esc_url($base . 'media/'), $markup);
    foreach (array('motion-map.html', 'design-system.html') as $doc) {
        $markup = str_replace('href="' . $doc . '"', 'href="' . esc_url($base . $doc) . '"', $markup);
    }
    $contact = get_theme_mod('dekoriya_contact_url', 'https://profi.ru/profile/SerdyukovaAI/');
    $markup = str_replace('https://profi.ru/profile/SerdyukovaAI/', esc_url($contact), $markup);
    $headline = get_theme_mod('dekoriya_headline', "Оформляем\nпространства\nдля бизнеса.");
    $lines = explode("\n", $headline);
    for ($i = 1; $i <= 3; $i++) {
        $markup = str_replace('{{HERO_LINE_' . $i . '}}', esc_html(isset($lines[$i - 1]) ? $lines[$i - 1] : ''), $markup);
    }
    return $markup;
}
