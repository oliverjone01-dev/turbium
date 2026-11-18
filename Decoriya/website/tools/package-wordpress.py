"""Package the canonical v9 runtime. Never ship a second, outdated implementation."""
from pathlib import Path
import re,json,shutil,zipfile,hashlib
R=Path(__file__).resolve().parents[1];theme=R/'wordpress/dekoriya-atelier';theme.mkdir(exist_ok=True,parents=True)
# Copy only the transitive assets needed by this homepage and the two case pages.
files=['index.html','v81.css','v81-site.css','v81.js','motion.css','v9.css','site-core.js','v9-motion.js','cases.json']
files += ['projects/'+p.name+'/index.html' for p in (R/'projects').iterdir() if p.is_dir()]
refs=set(files)
for rel in files:
 s=(R/rel).read_text()
 for ref in re.findall(r'(?:\.\./|\./)?assets/[A-Za-z0-9_./-]+\.(?:webp|svg|png|jpg|woff2?)',s):
  refs.add('assets/'+ref.split('assets/',1)[1])
# Full gallery images are named in embedded JSON. All assets above remain source-identical.
for rel in refs:
 src=R/rel;assert src.is_file(),rel;dst=theme/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
# Delete obsolete generated assets/runtime, preserving the theme only as a build product.
allowed=set(refs)|{'style.css','theme.json','functions.php','header.php','footer.php','front-page.php','index.php','template-parts/landing.html','screenshot.png','asset-manifest.json'}
for p in sorted(theme.rglob('*'),reverse=True):
 if p.is_file() and str(p.relative_to(theme)) not in allowed:p.unlink()
 elif p.is_dir() and not any(p.iterdir()):p.rmdir()
body=re.search(r'<body>(.*)</body>',(R/'index.html').read_text(),re.S)[1]
# Do not rewrite scripts/JSON with string-wide asset prefixes; use proper HTML URL attributes in PHP.
for i,line in enumerate(['Новогоднее','оформление','для бизнеса.'],1):body=body.replace('<span>'+line+'</span>','<span>{{HERO_LINE_'+str(i)+'}}</span>')
(theme/'template-parts').mkdir(exist_ok=True);(theme/'template-parts/landing.html').write_text(body)
(theme/'style.css').write_text('''/*
Theme Name: DEKORIYA Atelier Motion
Theme URI: https://github.com/oliverjone01-dev/turbium/tree/main/Decoriya/website
Author: DEKORIYA
Description: Новогодняя главная v9: адаптивная галерея, растровые схемы, лёгкие анимации и простой контакт.
Version: 9.4.0
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
    $c->add_setting('dekoriya_headline', array('default'=>"Новогоднее\\nоформление\\nдля бизнеса.",'sanitize_callback'=>'sanitize_textarea_field'));
    $c->add_control('dekoriya_headline', array('section'=>'dekoriya_main','label'=>'Заголовок hero (три строки)','type'=>'textarea'));
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
    $lines=explode("\\n",get_theme_mod('dekoriya_headline',"Новогоднее\\nоформление\\nдля бизнеса."));
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
    status_header(200);header('Content-Type: text/html; charset=UTF-8');echo $markup;exit;
});
''')
(theme/'header.php').write_text('''<?php if (!defined('ABSPATH')) { exit; } ?>
<!doctype html><html <?php language_attributes(); ?> data-version="9.0" data-build="9.4.0" data-motion="v9" data-asset-base="<?php echo esc_url(trailingslashit(get_template_directory_uri())); ?>" data-home-url="<?php echo esc_url(home_url('/')); ?>"><head><meta charset="<?php bloginfo('charset'); ?>"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><link rel="icon" href="<?php echo esc_url(get_template_directory_uri().'/assets/logo.svg'); ?>"><?php wp_head(); ?></head><body <?php body_class(); ?>><?php wp_body_open(); ?>
''')
(theme/'footer.php').write_text("<?php if (!defined('ABSPATH')) { exit; } wp_footer(); ?></body></html>")
(theme/'front-page.php').write_text("<?php if (!defined('ABSPATH')) { exit; } get_header(); echo dekoriya_render_landing(); get_footer();")
(theme/'index.php').write_text("<?php if (!defined('ABSPATH')) { exit; } get_header(); if(is_front_page()||is_home()){echo dekoriya_render_landing();}else{echo '<main class=\"case-page\">';while(have_posts()){the_post();the_title('<h1>','</h1>');the_content();}echo '</main>';}get_footer();")
(theme/'theme.json').write_text(json.dumps({'version':3,'settings':{'color':{'palette':[{'slug':k,'name':k,'color':v} for k,v in {'burgundy':'#57212f','ivory':'#f6f0e5','rose':'#e8d9d3'}.items()]},'layout':{'contentSize':'1312px'},'typography':{'fontFamilies':[{'slug':'golos','name':'Golos Text','fontFamily':'"Golos Text", sans-serif'}]}}},indent=2))
(theme/'asset-manifest.json').write_text(json.dumps({p:hashlib.sha256((theme/p).read_bytes()).hexdigest() for p in sorted(refs)},indent=2))
zip_path=R/'wordpress/dekoriya-atelier-v9.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(theme.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(theme.parent))
print(str(zip_path),round(zip_path.stat().st_size/1024/1024,2),'MiB;',len(refs),'canonical files')
