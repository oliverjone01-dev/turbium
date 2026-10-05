<?php
/**
 * Plugin Name: TURBIUM Landing
 * Description: Лендинг TURBIUM с локальной WebGL-сценой и демонстрационным отчётом. Shortcode: [turbium_landing].
 * Version: 1.2.0
 * Requires at least: 6.3
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) { exit; }
function turbium_landing_assets() {
    wp_register_style('turbium-fonts', plugins_url('assets/fonts.css', __FILE__), array(), '1.2.0');
    wp_register_style('turbium-landing', plugins_url('assets/style.css', __FILE__), array('turbium-fonts'), '1.2.0');
    wp_register_script('turbium-landing', plugins_url('assets/app.js', __FILE__), array(), '1.2.0', true);
}
add_action('wp_enqueue_scripts', 'turbium_landing_assets');
function turbium_landing_shortcode() {
    static $rendered = false;
    if ($rendered) { return ''; }
    $rendered = true;
    wp_enqueue_style('turbium-fonts');
    wp_enqueue_style('turbium-landing');
    wp_enqueue_script('turbium-landing');
    ob_start();
    wp_print_styles(array('turbium-fonts', 'turbium-landing'));
    $styles = ob_get_clean();
    $html = file_get_contents(plugin_dir_path(__FILE__) . 'page.html');
    if ($html === false) { return ''; }
    return $styles . str_replace('{{ASSET}}', esc_url(trailingslashit(plugins_url('assets', __FILE__))), $html);
}
add_shortcode('turbium_landing', 'turbium_landing_shortcode');
