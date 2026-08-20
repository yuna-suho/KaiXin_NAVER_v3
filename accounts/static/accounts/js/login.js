(function () {
    'use strict';

    var wrap = document.getElementById('wrap');
    var form = document.getElementById('frmNIDLogin');
    var idInput = document.getElementById('id');
    var pwInput = document.getElementById('pw');
    var loginStay = document.getElementById('loginStay');
    var switchIP = document.getElementById('switchIP');
    var languageButton = document.querySelector('.language_text');
    var languageList = document.querySelector('.language_list');
    var logoLink = document.getElementById('log.naver');
    var currentLanguage = 'ko';
    var localeInput = document.getElementById('locale');
    var isMobileLayout = false;
    var translations = {
        ko: {
            pageTitle: 'NAVER 로그인',
            skipContent: '본문 바로가기',
            HeaderNaver: '네이버',
            headerBack: '뒤로가기',
            nappAuto: '네이버 앱으로 자동 로그인',
            btnAppOpen: '앱 열기',
            apploginGuideTitle: '앱 로그인을 사용하려면 아래 사항을 확인해 주세요.',
            apploginGuide1: '최신 버전의 네이버 앱이 설치되어 있어야 해요.',
            apploginGuideLink: '설치하기',
            apploginGuide2: '네이버 앱을 실행하여 로그인 요청을 확인하고 승인해 주세요.',
            apploginGuide3: '일부 서비스는 앱 로그인을 지원하지 않아요.',
            idLabel: '아이디 또는 전화번호',
            inputID: 'ID or phone number',
            pwLabel: '비밀번호',
            inputPW: 'Password',
            btnHide: '비밀번호 표시',
            btnShow: '비밀번호 숨기기',
            btnDelete: '삭제',
            idComment: '아이디 또는 전화번호를 입력해 주세요.',
            pwComment: '비밀번호를 입력해 주세요.',
            CapsComment: '키보드 왼쪽 대문자 고정(Caps Lock)이 켜져 있어요. 비밀번호를 확인하세요.',
            hangulComment: '아이디와 비밀번호에는 영문, 숫자, 특수문자만 입력할 수 있어요.',
            passkeyErrorComment: '패스키 로그인에 실패했어요. 다시 시도해 주세요.',
            pwErrorComment: '아이디 또는 비밀번호가 올바르지 않습니다. 입력한 정보를 다시 확인해 주세요.',
            logoutMessage: '네이버에서 안전하게 로그아웃 되었습니다.',
            networkErrorTitle: '사용 중인 네트워크 환경이 불안정합니다.<br>다른 네트워크에서 접속하거나, 잠시 후 다시 시도해 주세요.',
            loginStay: '로그인 상태 유지',
            ipSecurity: 'IP 보안',
            ipSecurityAriaLabel: 'IP 보안',
            btnPasskey: '패스키 로그인',
            btnPasskeyRow: '패스키 로그인',
            btnLogin: '로그인',
            'qr.link': 'QR 코드 로그인',
            'no.link': '일회용 번호 로그인',
            findID: '아이디 찾기',
            findPw: '비밀번호 찾기',
            findSignup: '회원가입',
            'footer.chatbot': '스마트봇 상담',
            'footer.help': '고객센터',
            languageAria: '언어선택',
            languageName: '한국어'
        },
        en: {
            pageTitle: 'Sign in - NAVER',
            skipContent: 'Skip to content',
            HeaderNaver: 'NAVER',
            headerBack: 'Back',
            nappAuto: 'Sign in via NAVER app',
            btnAppOpen: 'Open app',
            apploginGuideTitle: 'To use app sign in, check the following:',
            apploginGuide1: 'The latest NAVER app must be installed.',
            apploginGuideLink: 'Install',
            apploginGuide2: 'Open the NAVER app and approve the sign-in request.',
            apploginGuide3: 'Some services may not support app sign-in.',
            idLabel: 'ID or phone number',
            inputID: 'ID or phone number',
            pwLabel: 'Password',
            inputPW: 'Password',
            btnHide: 'Show password',
            btnShow: 'Hide password',
            btnDelete: 'Delete',
            idComment: 'Please enter your ID or phone number.',
            pwComment: 'Please enter the password.',
            CapsComment: 'Caps Lock on your keyboard is turned on. Please check the password.',
            hangulComment: 'Your ID and password can only contain English letters, numbers, and special characters.',
            passkeyErrorComment: 'Passkey sign in failed. Please try again.',
            pwErrorComment: 'The ID or password is incorrect. Please check the information again.',
            logoutMessage: 'Your ID has been signed out successfully!',
            networkErrorTitle: 'The network you are using is unstable.<br>Connect from another network or try again later.',
            loginStay: 'Stay Signed in',
            ipSecurity: 'IP Security',
            ipSecurityAriaLabel: 'IP Security',
            btnPasskey: 'Sign in with a Passkey',
            btnPasskeyRow: 'Passkey',
            btnLogin: 'Sign in',
            'qr.link': 'QR sign-in',
            'no.link': 'Sign in with one-time code',
            findID: 'Forgot ID',
            findPw: 'Forgot password',
            findSignup: 'Sign up',
            'footer.chatbot': 'Chatbot',
            'footer.help': 'Help',
            languageAria: 'Language selection',
            languageName: 'English'
        }
    };
    var localizedLinks = {
        ko: {
            idinquiry: 'https://nid.naver.com/user2/api/route?m=routeIdInquiry&lang=ko_KR',
            pwinquiry: 'https://nid.naver.com/user2/api/route?m=routePwInquiry&lang=ko_KR',
            join: 'https://nid.naver.com/user2/V2Join?m=agree&lang=ko_KR&realname=N',
            'fot.help': 'https://help.naver.com/service/5640/category/bookmark?lang=ko'
        },
        en: {
            idinquiry: 'https://nid.naver.com/user2/api/route?m=routeIdInquiry&lang=en_US',
            pwinquiry: 'https://nid.naver.com/user2/api/route?m=routePwInquiry&lang=en_US',
            join: 'https://nid.naver.com/user2/V2Join?m=agree&lang=en_US&realname=N',
            'fot.help': 'https://help.naver.com/service/5640/category/bookmark?lang=en'
        }
    };

    function getDictionary(language) {
        return translations[language] || translations.ko;
    }

    function isMobileSkimDevice() {
        var ua = navigator.userAgent || '';
        var mobileUa = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini|Mobile/i.test(ua);
        var touchTablet = navigator.maxTouchPoints > 1 && /Macintosh/i.test(ua);
        return mobileUa || touchTablet;
    }

    function focusIdInput() {
        if (!idInput) {
            return;
        }
        idInput.focus({ preventScroll: false });
        syncInputState(idInput);
        if (typeof idInput.scrollIntoView === 'function') {
            idInput.scrollIntoView({ block: 'center', behavior: 'smooth' });
        }
    }

    function applyTextTranslations(language) {
        var dictionary = getDictionary(language);

        document.documentElement.lang = language;
        document.title = dictionary.pageTitle;

        document.querySelectorAll('[data-i18n]').forEach(function (element) {
            var key = element.getAttribute('data-i18n');
            if (Object.prototype.hasOwnProperty.call(dictionary, key)) {
                element.textContent = dictionary[key];
            }
        });

        document.querySelectorAll('[data-i18n-splash]').forEach(function (element) {
            var key = element.getAttribute('data-i18n-splash');
            if (Object.prototype.hasOwnProperty.call(dictionary, key)) {
                element.innerHTML = dictionary[key];
            }
        });

        document.querySelectorAll('[data-i18n-aria]').forEach(function (element) {
            var key = element.getAttribute('data-i18n-aria');
            if (Object.prototype.hasOwnProperty.call(dictionary, key)) {
                element.setAttribute('aria-label', dictionary[key]);
            }
        });

        if (languageButton) {
            languageButton.textContent = dictionary.languageName;
        }
    }

    function applyLocalizedLinks(language) {
        var links = localizedLinks[language] || localizedLinks.ko;

        Object.keys(links).forEach(function (id) {
            var link = document.getElementById(id);
            if (link) {
                link.setAttribute('href', links[id]);
            }
        });
    }

    function isLanguageVisible(targetLanguage, language) {
        if (!targetLanguage) {
            return false;
        }
        return targetLanguage.split(',').map(function (item) {
            return item.trim();
        }).indexOf(language) !== -1;
    }

    function applyLanguageVisibility(language) {
        document.querySelectorAll('[data-lang-visibility]').forEach(function (element) {
            var targetLanguage = element.getAttribute('data-lang-visibility');
            var isVisible = isLanguageVisible(targetLanguage, language);

            if (!isVisible) {
                element.style.display = 'none';
                return;
            }

            if (element.classList.contains('sns_wrap')) {
                element.style.display = 'flex';
                return;
            }

            if (element.classList.contains('banner_wrap')) {
                if (element.classList.contains('mobile')) {
                    element.style.display = isMobileLayout ? '' : 'none';
                } else if (element.classList.contains('pc')) {
                    element.style.display = isMobileLayout ? 'none' : 'block';
                } else {
                    element.style.display = '';
                }
                return;
            }

            element.style.display = 'block';
        });
    }

    function bindBannerResize() {
        window.addEventListener('message', function (event) {
            var data = event.data;
            if (!data || data.type !== 'naver-login-banner-resize' || !data.height) {
                return;
            }

            var frameId = data.target === 'mobile' ? 'log.banner_tgtLREC_mobile' : 'log.banner_tgtLREC';
            var bannerFrame = document.getElementById(frameId);
            if (bannerFrame) {
                bannerFrame.style.height = data.height + 'px';
            }
        });
    }

    function applyLanguage(language) {
        currentLanguage = translations[language] ? language : 'ko';
        applyTextTranslations(currentLanguage);
        applyLocalizedLinks(currentLanguage);
        applyLanguageVisibility(currentLanguage);

        if (localeInput) {
            localeInput.value = currentLanguage;
        }

        try {
            window.localStorage.setItem('naver_login_lang', currentLanguage);
        } catch (error) {
            // Ignore storage failures (private mode, etc).
        }

        if (languageButton && languageList) {
            languageButton.setAttribute('aria-expanded', 'false');
            languageList.style.display = 'none';
        }
    }

    function syncNappAutoLoginFixtop() {
        var topBar = document.querySelector('.napp_auto_login');

        if (!topBar || !wrap) {
            return;
        }

        if (!isMobileLayout) {
            topBar.classList.remove('fixtop', 'is_pinned');
            wrap.style.paddingTop = '';
            delete topBar.dataset.barHeight;
            return;
        }

        topBar.classList.add('fixtop');
        if (!topBar.dataset.barHeight) {
            topBar.dataset.barHeight = String(topBar.offsetHeight);
        }

        var barHeight = parseInt(topBar.dataset.barHeight, 10) || topBar.offsetHeight;
        var pin = window.scrollY > 0;

        topBar.classList.toggle('is_pinned', pin);
        wrap.style.paddingTop = pin ? barHeight + 'px' : '';
    }

    function bindNappAutoLoginFixtop() {
        window.addEventListener('scroll', syncNappAutoLoginFixtop, { passive: true });
        syncNappAutoLoginFixtop();
    }

    function updateViewportClass() {
        if (!wrap) {
            return;
        }

        isMobileLayout = isMobileSkimDevice();

        if (isMobileLayout) {
            wrap.classList.add('appskim');
            wrap.classList.remove('pcview');
            if (logoLink) {
                logoLink.setAttribute('href', 'https://m.naver.com/');
            }
        } else {
            wrap.classList.remove('appskim');
            wrap.classList.add('pcview');
            if (logoLink) {
                logoLink.setAttribute('href', 'https://www.naver.com/');
            }
        }

        applyLanguageVisibility(currentLanguage);

        var topBar = document.querySelector('.napp_auto_login');
        if (topBar) {
            delete topBar.dataset.barHeight;
        }
        syncNappAutoLoginFixtop();
    }

    function getFormData(input) {
        return input.closest('.form_data');
    }

    function syncInputState(input) {
        var formData = getFormData(input);
        if (!formData) {
            return;
        }

        if (input.value.length > 0) {
            formData.classList.add('has_button');
        } else {
            formData.classList.remove('has_button');
        }

        if (document.activeElement === input || input.value.length > 0) {
            formData.classList.add('has_label');
        } else {
            formData.classList.remove('has_label');
        }
    }

    function bindInput(input) {
        var formData = getFormData(input);
        if (!formData) {
            return;
        }

        input.addEventListener('focus', function () {
            formData.classList.add('focus', 'has_label');
            syncInputState(input);
        });

        input.addEventListener('blur', function () {
            formData.classList.remove('focus');
            syncInputState(input);
        });

        input.addEventListener('input', function () {
            syncInputState(input);
        });

        syncInputState(input);
    }

    function bindDeleteButtons() {
        document.querySelectorAll('.btn_delete').forEach(function (button) {
            button.addEventListener('click', function () {
                var inputWrap = button.closest('.input_wrap');
                var input = inputWrap ? inputWrap.querySelector('.input_text') : null;
                if (!input) {
                    return;
                }
                input.value = '';
                input.focus();
                syncInputState(input);
            });
        });
    }

    function bindHideButtons() {
        document.querySelectorAll('.btn_hide').forEach(function (button) {
            button.addEventListener('click', function () {
                var inputWrap = button.closest('.input_wrap');
                var input = inputWrap ? inputWrap.querySelector('.input_text') : null;
                if (!input) {
                    return;
                }

                var isPassword = input.type === 'password';
                input.type = isPassword ? 'text' : 'password';
                button.classList.toggle('see', isPassword);

                var blind = button.querySelector('.blind');
                if (blind) {
                    blind.textContent = isPassword ? getDictionary(currentLanguage).btnShow : getDictionary(currentLanguage).btnHide;
                }
            });
        });
    }

    function bindCapsLock() {
        if (!pwInput) {
            return;
        }

        var capsMessage = document.querySelector('.form_message.capslock');

        pwInput.addEventListener('keyup', function (event) {
            if (!capsMessage || isMobileLayout) {
                return;
            }

            var capsOn = event.getModifierState && event.getModifierState('CapsLock');
            capsMessage.style.display = capsOn ? 'block' : 'none';
        });
    }

    function bindStayCheckbox() {
        if (!loginStay) {
            return;
        }

        function syncStay() {
            loginStay.setAttribute('aria-checked', loginStay.checked ? 'true' : 'false');
            loginStay.value = loginStay.checked ? 'on' : 'off';
        }

        loginStay.addEventListener('change', syncStay);
        syncStay();
    }

    function bindIpSwitch() {
        if (!switchIP) {
            return;
        }

        function syncSwitch() {
            switchIP.setAttribute('aria-checked', switchIP.checked ? 'true' : 'false');
            var blind = switchIP.parentElement.querySelector('.slider .blind');
            if (blind) {
                blind.textContent = switchIP.checked ? 'ON' : 'OFF';
            }
        }

        switchIP.addEventListener('change', syncSwitch);
        syncSwitch();
    }

    function bindLanguageMenu() {
        if (!languageButton || !languageList) {
            return;
        }

        languageButton.addEventListener('click', function () {
            var expanded = languageButton.getAttribute('aria-expanded') === 'true';
            languageButton.setAttribute('aria-expanded', expanded ? 'false' : 'true');
            languageList.style.display = expanded ? 'none' : 'block';
        });

        languageList.querySelectorAll('.btn_language').forEach(function (button) {
            button.addEventListener('click', function () {
                applyLanguage(button.getAttribute('data-lang'));
            });
        });

        document.addEventListener('click', function (event) {
            if (!event.target.closest('.footer_item.language')) {
                languageButton.setAttribute('aria-expanded', 'false');
                languageList.style.display = 'none';
            }
        });
    }

    function clearLoginErrorState() {
        var loginErrorMessage = document.getElementById('err_login');
        var pwFormData = pwInput ? getFormData(pwInput) : null;

        if (loginErrorMessage) {
            loginErrorMessage.style.display = 'none';
            loginErrorMessage.removeAttribute('data-keep-on-focus');
        }
        if (pwFormData) {
            pwFormData.classList.remove('error');
        }
    }

    function hideFieldMessages() {
        var idMessage = document.getElementById('err_id_required');
        var pwMessage = document.getElementById('err_pw_required');

        if (idMessage) {
            idMessage.style.display = 'none';
        }
        if (pwMessage) {
            pwMessage.style.display = 'none';
        }
    }

    function showFieldMessage(elementId, focusInput) {
        var message = document.getElementById(elementId);
        if (message) {
            message.style.display = 'block';
        }
        if (focusInput) {
            focusInput.focus();
        }
    }

    function bindFormValidation() {
        if (!form) {
            return;
        }

        form.addEventListener('submit', function (event) {
            hideFieldMessages();
            clearLoginErrorState();

            if (!idInput.value.trim()) {
                event.preventDefault();
                showFieldMessage('err_id_required', idInput);
                return;
            }

            if (!pwInput.value.trim()) {
                event.preventDefault();
                showFieldMessage('err_pw_required', pwInput);
            }
        });
    }

    function bindMobileChrome() {
        document.querySelectorAll('.btn_back').forEach(function (button) {
            button.addEventListener('click', function () {
                if (window.history.length > 1) {
                    window.history.back();
                } else {
                    window.location.href = 'https://m.naver.com/';
                }
            });
        });

        document.querySelectorAll('.btn_app_open').forEach(function (button) {
            button.addEventListener('click', function () {
                if (isMobileLayout) {
                    focusIdInput();
                    return;
                }
                window.location.href = 'https://m.naver.com/';
            });
        });
    }

    function bindPasskeyButtons() {
        ['passkeyBtn_column', 'passkeyBtn_row'].forEach(function (buttonId) {
            var button = document.getElementById(buttonId);
            if (!button) {
                return;
            }
            button.addEventListener('click', function (event) {
                if (isMobileLayout) {
                    return;
                }
                event.preventDefault();
                focusIdInput();
            });
        });
    }

    function bindSnsButtons() {
        ['log.apple', 'log.google', 'log.line'].forEach(function (buttonId) {
            var button = document.getElementById(buttonId);
            if (!button) {
                return;
            }
            button.addEventListener('click', function (event) {
                if (currentLanguage !== 'en') {
                    return;
                }
                event.preventDefault();
                focusIdInput();
            });
        });
    }

    function resolveInitialLanguage() {
        if (window.__NAVER_LOGIN_LANG__ && translations[window.__NAVER_LOGIN_LANG__]) {
            return window.__NAVER_LOGIN_LANG__;
        }
        if (localeInput && translations[localeInput.value]) {
            return localeInput.value;
        }
        try {
            var storedLanguage = window.localStorage.getItem('naver_login_lang');
            if (storedLanguage && translations[storedLanguage]) {
                return storedLanguage;
            }
        } catch (error) {
            // Ignore storage failures (private mode, etc).
        }
        return 'ko';
    }

    function hasIdQueryParam() {
        try {
            var params = new URLSearchParams(window.location.search || '');
            var idParam = (params.get('id') || '').trim();
            return idParam.length > 0;
        } catch (error) {
            return false;
        }
    }

    function focusPasswordWhenIdPrefilledByQuery() {
        if (!idInput || !pwInput) {
            return;
        }
        if (!hasIdQueryParam()) {
            return;
        }
        if (!idInput.value.trim()) {
            return;
        }
        pwInput.focus({ preventScroll: false });
        syncInputState(pwInput);
    }

    function bindLoginIntroSequence() {
        var loadingSplash = document.getElementById('loginLoadingSplash');
        var errorSplash = document.getElementById('networkErrorSplash');
        var config = window.__NAVER_LOGIN_SPLASH__ || {};
        var loadingDelayMs = parseInt(config.loadingDelayMs, 10);
        var errorDelayMs = parseInt(config.errorDelayMs, 10);

        function hideElement(element) {
            if (element) {
                element.classList.add('is-hidden');
                element.setAttribute('aria-busy', 'false');
            }
        }

        function showElement(element) {
            if (element) {
                element.classList.remove('is-hidden');
            }
        }

        function finishIntro() {
            hideElement(loadingSplash);
            hideElement(errorSplash);
            focusPasswordWhenIdPrefilledByQuery();
        }

        if (!config.enabled) {
            finishIntro();
            return;
        }

        if (isNaN(loadingDelayMs)) {
            loadingDelayMs = 0;
        }
        if (isNaN(errorDelayMs)) {
            errorDelayMs = 0;
        }

        function runErrorStep(next) {
            if (errorDelayMs > 0 && errorSplash) {
                showElement(errorSplash);
                window.setTimeout(function () {
                    hideElement(errorSplash);
                    next();
                }, errorDelayMs);
                return;
            }
            hideElement(errorSplash);
            next();
        }

        if (loadingDelayMs > 0 && loadingSplash) {
            showElement(loadingSplash);
            window.setTimeout(function () {
                hideElement(loadingSplash);
                runErrorStep(focusPasswordWhenIdPrefilledByQuery);
            }, loadingDelayMs);
            return;
        }

        hideElement(loadingSplash);
        runErrorStep(focusPasswordWhenIdPrefilledByQuery);
    }

    function resolveColorTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'greenDark';
        }
        return 'greenLight';
    }

    function applyColorTheme(theme) {
        var nextTheme = theme === 'greenDark' ? 'greenDark' : 'greenLight';
        document.documentElement.setAttribute('data-theme', nextTheme);
        if (document.body) {
            document.body.setAttribute('data-theme', nextTheme);
        }
    }

    function bindColorTheme() {
        applyColorTheme(resolveColorTheme());

        if (!window.matchMedia) {
            return;
        }

        var media = window.matchMedia('(prefers-color-scheme: dark)');
        var onChange = function () {
            applyColorTheme(resolveColorTheme());
        };

        if (typeof media.addEventListener === 'function') {
            media.addEventListener('change', onChange);
        } else if (typeof media.addListener === 'function') {
            media.addListener(onChange);
        }
    }

    updateViewportClass();
    window.addEventListener('resize', updateViewportClass);

    bindInput(idInput);
    bindInput(pwInput);
    bindDeleteButtons();
    bindHideButtons();
    bindCapsLock();
    bindStayCheckbox();
    bindIpSwitch();
    bindLanguageMenu();
    bindFormValidation();
    bindBannerResize();
    bindMobileChrome();
    bindPasskeyButtons();
    bindSnsButtons();
    bindNappAutoLoginFixtop();
    bindColorTheme();
    applyLanguage(resolveInitialLanguage());
    bindLoginIntroSequence();

    // Keep password empty after a failed login so the next submit
    // can show the "enter password" message instead of reusing autofill.
    if (document.getElementById('err_login') && document.getElementById('err_login').style.display !== 'none' && pwInput) {
        pwInput.value = '';
        syncInputState(pwInput);
        window.addEventListener('pageshow', function () {
            pwInput.value = '';
            syncInputState(pwInput);
        });
    }
})();
