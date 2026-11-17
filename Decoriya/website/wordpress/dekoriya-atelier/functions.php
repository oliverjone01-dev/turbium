<?php
if (!defined('ABSPATH')) { exit; }
add_action('after_setup_theme', function () {
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('html5', array('search-form','comment-form','gallery','caption','style','script'));
});
add_action('wp_enqueue_scripts', function () {
    $uri = get_template_directory_uri();
    $previous = array();
    foreach (array('v81.css','v81-site.css','motion.css','v9.css') as $i => $file) {
        $handle = 'dekoriya-style-' . $i;
        wp_enqueue_style($handle, $uri . '/' . $file, $previous, hash_file('sha256', get_template_directory() . '/' . $file));
        $previous = array($handle);
    }
    wp_enqueue_script('dekoriya-core', $uri . '/site-core.js', array(), hash_file('sha256', get_template_directory() . '/site-core.js'), array('in_footer'=>true,'strategy'=>'defer'));
    wp_enqueue_script('dekoriya-motion', $uri . '/v9-motion.js', array('dekoriya-core'), hash_file('sha256', get_template_directory() . '/v9-motion.js'), array('in_footer'=>true,'strategy'=>'defer'));
});
add_action('customize_register', function ($c) {
    $c->add_section('dekoriya_main', array('title'=>'Декория: главная','priority'=>30));
    $c->add_setting('dekoriya_headline', array('default'=>"Новогоднее\nоформление\nдля бизнеса.",'sanitize_callback'=>'sanitize_textarea_field'));
    $c->add_control('dekoriya_headline', array('section'=>'dekoriya_main','label'=>'Заголовок hero (три строки)','type'=>'textarea'));
    $c->add_setting('dekoriya_contact_url', array('default'=>'https://profi.ru/profile/SerdyukovaAI/','sanitize_callback'=>'esc_url_raw'));
    $c->add_control('dekoriya_contact_url', array('section'=>'dekoriya_main','label'=>'Ссылка обращения','type'=>'url'));
});
add_filter('pre_get_document_title', function ($title) { return is_front_page() ? 'Новогоднее оформление для бизнеса в Москве и области | Декория' : $title; });
add_action('wp',function(){if(is_front_page())remove_action('wp_head','rel_canonical');});
add_action('wp_head', function () {
    if (!is_front_page()) { return; }
    echo '<link rel="canonical" href="'.esc_url(home_url('/')).'">';
    $title='Новогоднее оформление для бизнеса в Москве и области | Декория';
    $description='Студия Олеси Овакимян оформляет входные группы, витрины и интерьеры в Москве и области. От эскиза до монтажа.';
    echo '<meta name="description" content="'.esc_attr($description).'">';
    echo '<meta property="og:title" content="'.esc_attr($title).'">';
    echo '<meta property="og:description" content="'.esc_attr($description).'">';
    echo '<meta property="og:type" content="website"><meta property="og:url" content="'.esc_url(home_url('/')).'">';
    echo '<meta property="og:image" content="'.esc_url(get_template_directory_uri().'/assets/v81/182-1911-0d2f6.webp').'">';
    echo '<script type="application/ld+json">'.wp_json_encode(array('@context'=>'https://schema.org','@type'=>'WebSite','name'=>'Декория','url'=>home_url('/')),JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES).'</script>';
    echo '<link rel="preload" as="font" type="font/woff2" crossorigin href="'.esc_url(get_template_directory_uri().'/assets/golos-regular.woff2').'">';
});
function dekoriya_render_landing() {
    $markup=file_get_contents(get_template_directory().'/template-parts/landing.html');
    $base=trailingslashit(get_template_directory_uri());
    // HTML attributes including srcset and inline CSS masks. JSON stays relative to data-asset-base.
    $markup=str_replace(array('src="./assets/','href="./assets/','srcset="./assets/',', ./assets/','&quot;./assets/'),array('src="'.esc_url($base).'assets/','href="'.esc_url($base).'assets/','srcset="'.esc_url($base).'assets/',', '.esc_url($base).'assets/','&quot;'.esc_url($base).'assets/'),$markup);
    $cases=json_decode(file_get_contents(get_template_directory().'/cases.json'),true);
    foreach ($cases as $case) {
        $markup=str_replace('href="./projects/'.$case['id'].'/"','href="'.esc_url(add_query_arg('dk_project',$case['id'],home_url('/'))).'"',$markup);
    }
    $markup=str_replace('https://profi.ru/profile/SerdyukovaAI/',esc_url(get_theme_mod('dekoriya_contact_url','https://profi.ru/profile/SerdyukovaAI/')),$markup);
    $lines=explode("\n",get_theme_mod('dekoriya_headline',"Новогоднее\nоформление\nдля бизнеса."));
    for($i=1;$i<=3;$i++){$markup=str_replace('{{HERO_LINE_'.$i.'}}',esc_html($lines[$i-1]??''),$markup);}
    return $markup;
}
add_action('template_redirect',function(){
    if(!isset($_GET['dk_project']))return;
    if(!is_string($_GET['dk_project'])){wp_die('Проект не найден.','Декория',array('response'=>404));}
    $id=sanitize_key(wp_unslash($_GET['dk_project']));
    $cases=json_decode(file_get_contents(get_template_directory().'/cases.json'),true);
    if(!in_array($id,array_column($cases,'id'),true)){wp_die('Проект не найден.','Декория',array('response'=>404));}
    $markup=file_get_contents(get_template_directory().'/projects/'.$id.'/index.html');
    $base=trailingslashit(get_template_directory_uri());
    $markup=str_replace('../../assets/',$base.'assets/',$markup);
    foreach(array('v81.css','v81-site.css','v81.js') as $f){$markup=str_replace('../../'.$f,$base.$f,$markup);}
    $markup=str_replace(array('../../?','../../#','href="../../"'),array(home_url('/').'?',home_url('/').'#','href="'.esc_url(home_url('/')).'"'),$markup);
    $markup=str_replace('? case=','?case=',$markup);
    $markup=str_replace('https://oliverjone01-dev.github.io/turbium/Decoriya/website/projects/'.$id.'/',esc_url(add_query_arg('dk_project',$id,home_url('/'))),$markup);
    $markup=str_replace('https://profi.ru/profile/SerdyukovaAI/',esc_url(get_theme_mod('dekoriya_contact_url','https://profi.ru/profile/SerdyukovaAI/')),$markup);
    status_header(200);header('Content-Type: text/html; charset=UTF-8');echo $markup;exit;
});
