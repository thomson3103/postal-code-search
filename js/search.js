/**
 * 郵便番号検索 - search.js
 * クライアントサイド検索エンジン
 * 都道府県別JSONチャンクを遅延読み込みしてインクリメンタルサーチ
 */
(function() {
  'use strict';

  // --- 都道府県コード→スラッグのマッピング ---
  var PREF_CODES = {
    '01':'hokkaido','02':'aomori','03':'iwate','04':'miyagi','05':'akita',
    '06':'yamagata','07':'fukushima','08':'ibaraki','09':'tochigi','10':'gunma',
    '11':'saitama','12':'chiba','13':'tokyo','14':'kanagawa','15':'niigata',
    '16':'toyama','17':'ishikawa','18':'fukui','19':'yamanashi','20':'nagano',
    '21':'gifu','22':'shizuoka','23':'aichi','24':'mie','25':'shiga',
    '26':'kyoto','27':'osaka','28':'hyogo','29':'nara','30':'wakayama',
    '31':'tottori','32':'shimane','33':'okayama','34':'hiroshima','35':'yamaguchi',
    '36':'tokushima','37':'kagawa','38':'ehime','39':'kochi','40':'fukuoka',
    '41':'saga','42':'nagasaki','43':'kumamoto','44':'oita','45':'miyazaki',
    '46':'kagoshima','47':'okinawa'
  };

  // キャッシュ: { prefCode: [data] }
  var cache = {};
  var loadingPref = {};

  /**
   * 都道府県JSONを読み込む
   */
  function loadPrefData(prefCode) {
    if (cache[prefCode]) return Promise.resolve(cache[prefCode]);
    if (loadingPref[prefCode]) return loadingPref[prefCode];

    var slug = PREF_CODES[prefCode];
    if (!slug) return Promise.resolve([]);

    loadingPref[prefCode] = fetch('/data/search/' + prefCode + '-' + slug + '.json')
      .then(function(res) { return res.json(); })
      .then(function(data) {
        cache[prefCode] = data;
        delete loadingPref[prefCode];
        return data;
      })
      .catch(function() {
        delete loadingPref[prefCode];
        return [];
      });

    return loadingPref[prefCode];
  }

  /**
   * 全都道府県をロード（全国検索用）
   */
  function loadAllData() {
    var codes = Object.keys(PREF_CODES);
    return Promise.all(codes.map(loadPrefData)).then(function(results) {
      var all = [];
      results.forEach(function(r) { all = all.concat(r); });
      return all;
    });
  }

  /**
   * 郵便番号から都道府県コードを推定（上1〜2桁）
   * 郵便番号の上位桁と都道府県の対応は厳密ではないため、
   * 番号検索は全データから前方一致で行う
   */
  function isZipcodeQuery(q) {
    return /^[\d\-ー−]{1,8}$/.test(q);
  }

  /**
   * 検索を実行
   */
  function search(query, maxResults) {
    maxResults = maxResults || 20;
    var q = query.trim();
    if (q.length < 2) return Promise.resolve([]);

    // 郵便番号検索
    if (isZipcodeQuery(q)) {
      var numOnly = q.replace(/[\-ー−]/g, '');
      return loadAllData().then(function(data) {
        var results = [];
        for (var i = 0; i < data.length && results.length < maxResults; i++) {
          if (data[i].z.indexOf(numOnly) === 0) {
            results.push(data[i]);
          }
        }
        return results;
      });
    }

    // 住所検索（漢字・カナ）
    return loadAllData().then(function(data) {
      var qLower = q.toLowerCase();
      var results = [];
      for (var i = 0; i < data.length && results.length < maxResults; i++) {
        var addr = (data[i].a || '').toLowerCase();
        var kana = (data[i].k || '').toLowerCase();
        if (addr.indexOf(qLower) !== -1 || kana.indexOf(qLower) !== -1) {
          results.push(data[i]);
        }
      }
      return results;
    });
  }

  /**
   * 郵便番号をフォーマット（XXX-XXXX）
   */
  function formatZip(code) {
    if (code.length === 7) return code.slice(0, 3) + '-' + code.slice(3);
    return code;
  }

  /**
   * プレビュー結果をHTMLに変換
   */
  function renderResults(results, container) {
    if (!results.length) {
      container.innerHTML = '<div class="sp-empty">該当する郵便番号が見つかりません</div>';
      container.hidden = false;
      return;
    }

    var html = '<ul class="sp-list">';
    results.forEach(function(r) {
      html += '<li><a href="/zipcode/' + r.z + '/">'
        + '<span class="sp-zip">〒' + formatZip(r.z) + '</span>'
        + '<span class="sp-addr">' + escapeHtml(r.a) + '</span>'
        + '</a></li>';
    });
    html += '</ul>';
    container.innerHTML = html;
    container.hidden = false;
  }

  function escapeHtml(str) {
    var div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  // --- インクリメンタルサーチのセットアップ ---
  var debounceTimer;

  function setupSearch(inputId, previewId) {
    var input = document.getElementById(inputId);
    var preview = document.getElementById(previewId);
    if (!input || !preview) return;

    input.addEventListener('input', function() {
      clearTimeout(debounceTimer);
      var q = this.value.trim();

      if (q.length < 2) {
        preview.hidden = true;
        return;
      }

      debounceTimer = setTimeout(function() {
        search(q, 10).then(function(results) {
          renderResults(results, preview);
        });
      }, 300);
    });

    // 外側クリックで閉じる
    document.addEventListener('click', function(e) {
      if (!input.contains(e.target) && !preview.contains(e.target)) {
        preview.hidden = true;
      }
    });

    // フォーカスで再表示
    input.addEventListener('focus', function() {
      if (preview.innerHTML && this.value.trim().length >= 2) {
        preview.hidden = false;
      }
    });

    // Escで閉じる
    input.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') {
        preview.hidden = true;
      }
    });
  }

  // --- 初期化 ---
  document.addEventListener('DOMContentLoaded', function() {
    // トップページの検索
    setupSearch('top-search-input', 'search-results-preview');

    // ヘッダーの検索（全ページ共通）にもプレビューを追加
    var headerInput = document.getElementById('header-search-input');
    if (headerInput) {
      // ヘッダー用プレビューコンテナを動的に追加
      var headerForm = headerInput.closest('.search-form');
      if (headerForm) {
        var headerPreview = document.createElement('div');
        headerPreview.id = 'header-search-preview';
        headerPreview.className = 'search-preview';
        headerPreview.hidden = true;
        headerForm.parentNode.style.position = 'relative';
        headerForm.parentNode.appendChild(headerPreview);
        setupSearch('header-search-input', 'header-search-preview');
      }
    }
  });

  // スタイル（JSから注入、search.jsが読まれた時のみ適用）
  var style = document.createElement('style');
  style.textContent = [
    '.sp-list{list-style:none;margin:0;padding:0}',
    '.sp-list li{border-bottom:1px solid #eee}',
    '.sp-list li:last-child{border-bottom:none}',
    '.sp-list a{display:flex;gap:12px;padding:10px 14px;text-decoration:none;transition:background .1s}',
    '.sp-list a:hover{background:#fff0f0}',
    '.sp-zip{font-weight:600;white-space:nowrap;color:#cc0000;font-size:.9rem}',
    '.sp-addr{color:#333;font-size:.85rem}',
    '.sp-empty{padding:14px;text-align:center;color:#999;font-size:.85rem}',
  ].join('');
  document.head.appendChild(style);
})();
