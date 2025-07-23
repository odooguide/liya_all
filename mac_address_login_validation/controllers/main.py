import logging
import sys
import subprocess
import re

try:
    from getmac import get_mac_address as gma
except ImportError:
    _logger = logging.getLogger(__name__)
    _logger.info("getmac modülü bulunamadı, yüklenecek…")
    py_v = f"python{sys.version_info.major}.{sys.version_info.minor}"
    subprocess.check_call([py_v, "-m", "pip", "install", "getmac"])
    from getmac import get_mac_address as gma

import odoo
from odoo import http
from odoo.http import request
from odoo.tools.translate import _

from odoo.addons.web.controllers.home import (
    Home as BaseHome,
    ensure_db,
    SIGN_UP_REQUEST_PARAMS,
    CREDENTIAL_PARAMS,
    _get_login_redirect_url,
)

_logger = logging.getLogger(__name__)

class Home(BaseHome):
    @http.route('/web/login', type='http', auth="none", readonly=False)
    def web_login(self, redirect=None, **kw):
        ensure_db()
        request.params['login_success'] = False

        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return request.redirect(redirect)

        if request.env.uid is None:
            if request.session.uid is None:
                request.env["ir.http"]._auth_method_public()
            else:
                request.update_env(user=request.session.uid)

        values = {k: v for k, v in request.params.items() if k in SIGN_UP_REQUEST_PARAMS}
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            old_uid = request.session.uid

            ip_address = request.httprequest.environ.get('REMOTE_ADDR')
            mac_address = self._get_mac_from_ip(ip_address)
            

            login = request.params.get('login')
            _logger.info(f"Giriş denemesi: user={login}, ip={ip_address}, mac={mac_address}")
            if login:
                user_rec = request.env['res.users'].sudo().search(
                    [('login', '=', login)], limit=1
                )
                if user_rec.mac_address_login_toggle:
                    allowed = user_rec.mac_address_ids.mapped('mac_address')
                    if mac_address not in allowed:
                        request.update_env(user=old_uid)
                        values['error'] = _("Bu cihazdan giriş yapmaya izniniz yok")
                        return self._render_login(values)

            try:
                credential = {
                    k: v for k, v in request.params.items()
                    if k in CREDENTIAL_PARAMS and v
                }
                credential.setdefault('type', 'password')
                auth_info = request.session.authenticate(request.db, credential)
                request.env['res.users'].sudo().browse(auth_info['uid']).write({'current_mac_address': mac_address})
                request.params['login_success'] = True
                return request.redirect(
                    _get_login_redirect_url(auth_info['uid'], redirect=redirect)
                )
            except odoo.exceptions.AccessDenied as e:
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['error'] = _("Wrong login/password")
                else:
                    values['error'] = e.args[0]

        response = request.render('web.login', values)
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response
    
    def _render_login(self, values):
        """Ortak login render ve header ayarları."""
        response = request.render('web.login', values)
        response.headers.update({
            'Cache-Control': 'no-cache',
            'X-Frame-Options': 'SAMEORIGIN',
            'Content-Security-Policy': "frame-ancestors 'self'"
        })
        return response

    def _get_mac_from_ip(self, ip):
        """
        Aynı LAN’da isek IP’den MAC döner.
        - ping ile ARP tablosuna ekleme
        - önce getmac(ip=...) dener, sonra fallback arp komutu
        """
        if not ip:
            return None
        try:
            # ARP tablosuna eklemek için ping
            subprocess.call(['ping', '-c', '1', ip],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # getmac kütüphanesiyle al
            mac = gma(ip=ip)
            if mac:
                return mac
            # fallback arp sorgusu
            out = subprocess.check_output(['arp', '-n', ip]).decode()
            m = re.search(r'([0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5})', out)
            mac = m.group(1) if m else None
            _logger.debug(f"ARP çıktısından IP={ip} için bulunan MAC: {mac}")
            if mac:
                _logger.info(f"IP {ip} → MAC {mac} (ARP fallback)")
            else:
                _logger.warning(f"IP {ip} için MAC bulunamadı (ARP fallback).")
            return mac
        
        except Exception as e:
            _logger.warning(f"MAC alınamadı ({ip}): {e}")
            return None
