const GITHUB_OWNER = 'militzerjoseph';
const GITHUB_REPO = 'pincas';
const GITHUB_WORKFLOW = 'build-shortcut-builder.yml';
const GITHUB_REF = 'shortcut-builder-trial';
const DAILY_BUILD_LIMIT = 20;

function doGet() {
  return json_({ ok: true, service: 'shortcut-builder-dispatch' });
}

function doPost(e) {
  try {
    var body = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    var appName = String(body.app_name || '').trim();
    var appUrl = String(body.app_url || '').trim();
    var zoom = parseInt(body.app_zoom || 90, 10);
    var requestId = String(body.request_id || Utilities.getUuid()).trim();

    if (!appName || appName.length > 60) {
      return json_({ ok: false, error: 'invalid_app_name' });
    }
    if (!/^https?:\/\//i.test(appUrl) || appUrl.length > 2000) {
      return json_({ ok: false, error: 'invalid_app_url' });
    }
    if (isNaN(zoom) || zoom < 50 || zoom > 150) {
      return json_({ ok: false, error: 'invalid_zoom' });
    }
    if (!/^[A-Za-z0-9._-]{1,80}$/.test(requestId)) {
      return json_({ ok: false, error: 'invalid_request_id' });
    }

    var limit = useDailyQuota_();
    if (!limit.ok) {
      return json_({ ok: false, error: 'daily_limit_reached' });
    }

    var token = PropertiesService.getScriptProperties().getProperty('GITHUB_TOKEN');
    if (!token) {
      return json_({ ok: false, error: 'github_token_missing' });
    }

    var apiUrl = 'https://api.github.com/repos/' + GITHUB_OWNER + '/' + GITHUB_REPO +
      '/actions/workflows/' + encodeURIComponent(GITHUB_WORKFLOW) + '/dispatches';

    var payload = {
      ref: GITHUB_REF,
      inputs: {
        app_name: appName,
        app_url: appUrl,
        app_zoom: String(zoom),
        request_id: requestId
      }
    };

    var response = UrlFetchApp.fetch(apiUrl, {
      method: 'post',
      contentType: 'application/json',
      payload: JSON.stringify(payload),
      headers: {
        Authorization: 'Bearer ' + token,
        Accept: 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
      },
      muteHttpExceptions: true
    });

    var status = response.getResponseCode();
    if (status === 204) {
      return json_({
        ok: true,
        request_id: requestId,
        app_name: appName,
        app_zoom: zoom,
        remaining_today: limit.remaining
      });
    }

    return json_({
      ok: false,
      error: 'github_dispatch_failed',
      status: status
    });
  } catch (err) {
    return json_({ ok: false, error: 'server_error' });
  }
}

function useDailyQuota_() {
  var props = PropertiesService.getScriptProperties();
  var day = Utilities.formatDate(new Date(), 'Etc/UTC', 'yyyy-MM-dd');
  var key = 'build_count_' + day;
  var count = parseInt(props.getProperty(key) || '0', 10);
  if (count >= DAILY_BUILD_LIMIT) {
    return { ok: false, remaining: 0 };
  }
  count += 1;
  props.setProperty(key, String(count));
  return { ok: true, remaining: DAILY_BUILD_LIMIT - count };
}

function json_(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
