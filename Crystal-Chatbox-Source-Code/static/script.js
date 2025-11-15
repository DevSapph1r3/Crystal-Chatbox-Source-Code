let refreshInterval = (window.CONFIG && window.CONFIG.refresh_interval) || 1;
let updateTimer;
let customMessages = [];

document.addEventListener('DOMContentLoaded', () => {
    setupTabs();
    setupButtons();
    setupLayout();
    setupProgressStyle();
    setupAdvanced();
    setupStreamerMode();
    loadCustomMessages();
    startUpdate();
});

function setupTabs() {
    document.getElementById('dashboard_tab').addEventListener('click', () => showTab('dashboard'));
    document.getElementById('settings_tab').addEventListener('click', () => showTab('settings'));
    document.getElementById('advanced_tab').addEventListener('click', () => showTab('advanced'));
}

function showTab(tab) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tabcontent').forEach(tc => tc.style.display = 'none');
    
    if (tab === 'dashboard') {
        document.getElementById('dashboard_tab').classList.add('active');
        document.getElementById('dashboard_content').style.display = 'block';
    } else if (tab === 'settings') {
        document.getElementById('settings_tab').classList.add('active');
        document.getElementById('settings_content').style.display = 'block';
        loadCustomMessages();
    } else if (tab === 'advanced') {
        document.getElementById('advanced_tab').classList.add('active');
        document.getElementById('advanced_content').style.display = 'block';
        loadPerMessageTimings();
        loadMessageWeights();
    }
}

function setupButtons() {
    document.getElementById('btn_chatbox').addEventListener('click', toggleChatbox);
    document.getElementById('btn_time').addEventListener('click', toggleTime);
    document.getElementById('btn_custom').addEventListener('click', toggleCustom);
    document.getElementById('btn_music').addEventListener('click', toggleMusic);
    document.getElementById('btn_window').addEventListener('click', toggleWindow);
    document.getElementById('btn_heartrate').addEventListener('click', toggleHeartRate);
    document.getElementById('btn_weather').addEventListener('click', toggleWeather);
    document.getElementById('btn_music_progress').addEventListener('click', toggleMusicProgress);
}

function setupStreamerMode() {
    const streamerModeEnabled = document.getElementById('toggle_streamer_btn')?.textContent.includes('ON');
    
    if (streamerModeEnabled) {
        const sensitiveFields = [
            document.querySelector('input[name="quest_ip"]'),
            document.querySelector('input[name="spotify_client_id"]'),
            document.querySelector('input[name="spotify_client_secret"]')
        ];
        
        sensitiveFields.forEach(field => {
            if (field && field.value && !field.value.includes('***')) {
                field.type = 'password';
                
                const container = field.parentElement;
                let revealBtn = container.querySelector('.reveal-btn');
                
                if (!revealBtn) {
                    revealBtn = document.createElement('button');
                    revealBtn.type = 'button';
                    revealBtn.className = 'reveal-btn btn-on';
                    revealBtn.textContent = '👁';
                    revealBtn.style.marginLeft = '8px';
                    revealBtn.style.padding = '4px 12px';
                    
                    let isRevealed = false;
                    revealBtn.addEventListener('click', (e) => {
                        e.preventDefault();
                        isRevealed = !isRevealed;
                        field.type = isRevealed ? 'text' : 'password';
                        revealBtn.textContent = isRevealed ? '👁‍🗨' : '👁';
                    });
                    
                    field.after(revealBtn);
                }
            }
        });
    }
}

function setupAdvanced() {
    document.getElementById('random_order_btn').addEventListener('click', async (e) => {
        await fetch('/toggle_random_order', { method: 'POST' });
        await updateAdvancedButtons();
        updateMessageWeightsVisibility();
    });
    
    document.getElementById('show_module_icons_btn').addEventListener('click', async (e) => {
        await fetch('/toggle_module_icons', { method: 'POST' });
        await updateAdvancedButtons();
    });
    
    document.getElementById('toggle_theme_btn').addEventListener('click', async () => {
        const response = await fetch('/toggle_theme', { method: 'POST' });
        const data = await response.json();
        document.body.className = data.theme === 'light' ? 'light' : '';
        updateDisplayOptionButtons();
    });
    
    document.getElementById('toggle_streamer_btn').addEventListener('click', async () => {
        await fetch('/toggle_streamer_mode', { method: 'POST' });
        updateDisplayOptionButtons();
        location.reload();
    });
    
    document.getElementById('toggle_compact_btn').addEventListener('click', async () => {
        await fetch('/toggle_compact_mode', { method: 'POST' });
        updateDisplayOptionButtons();
        location.reload();
    });
    
    document.getElementById('download_settings_btn').addEventListener('click', () => {
        window.location.href = '/download_settings';
    });
    
    document.getElementById('upload_settings_btn').addEventListener('click', () => {
        document.getElementById('upload_settings_file').click();
    });
    
    document.getElementById('upload_settings_file').addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        try {
            const text = await file.text();
            const settings = JSON.parse(text);
            
            const response = await fetch('/upload_settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(settings)
            });
            
            if (response.ok) {
                alert('Settings uploaded successfully! Reloading page...');
                location.reload();
            } else {
                alert('Failed to upload settings. Please check the file format.');
            }
        } catch (error) {
            alert('Invalid settings file. Please upload a valid JSON file.');
        }
        
        e.target.value = '';
    });
    
    document.getElementById('download_log_btn').addEventListener('click', () => {
        window.location.href = '/download_log';
    });
    
    document.getElementById('reset_defaults_btn').addEventListener('click', async () => {
        if (confirm('Reset all settings to defaults? This cannot be undone.')) {
            await fetch('/reset_settings', { method: 'POST' });
            location.reload();
        }
    });
    
    document.getElementById('add_message_btn').addEventListener('click', async () => {
        const newText = prompt('Enter new message:');
        if (newText && newText.trim()) {
            await fetch('/add_custom_message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: newText.trim() })
            });
            loadCustomMessages();
            loadPerMessageTimings();
            loadMessageWeights();
        }
    });
    
    document.getElementById('toggle_window_tracking_btn').addEventListener('click', async () => {
        const response = await fetch('/toggle_window_tracking', { method: 'POST' });
        const data = await response.json();
        const btn = document.getElementById('toggle_window_tracking_btn');
        btn.className = data.window_tracking_enabled ? 'btn-on' : 'btn-off';
        btn.textContent = `Window Tracking: ${data.window_tracking_enabled ? 'ON' : 'OFF'}`;
    });
    
    document.getElementById('window_tracking_mode').addEventListener('change', async (e) => {
        const mode = e.target.value;
        await fetch('/save_window_tracking_mode', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode })
        });
    });
    
    document.getElementById('save_emojis_btn').addEventListener('click', async () => {
        const timeEmoji = document.getElementById('time_emoji').value;
        const songEmoji = document.getElementById('song_emoji').value;
        const windowEmoji = document.getElementById('window_emoji').value;
        const heartrateEmoji = document.getElementById('heartrate_emoji').value;
        
        await fetch('/save_emoji_settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                time_emoji: timeEmoji,
                song_emoji: songEmoji,
                window_emoji: windowEmoji,
                heartrate_emoji: heartrateEmoji
            })
        });
        alert('Emojis saved successfully!');
    });
    
    document.getElementById('toggle_patreon_btn').addEventListener('click', async () => {
        const response = await fetch('/status');
        const data = await response.json();
        const isSupporter = data.patreon_supporter;
        
        if (isSupporter) {
            if (confirm('Remove Patreon supporter status?')) {
                const removeResponse = await fetch('/remove_patreon_supporter', { method: 'POST' });
                const removeData = await removeResponse.json();
                updatePatreonUI(removeData.patreon_supporter);
            }
        } else {
            const code = prompt('Enter your Patreon supporter code:\n\n(Get your code from the Patreon page)');
            if (code) {
                const verifyResponse = await fetch('/verify_patreon_supporter', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code: code })
                });
                const verifyData = await verifyResponse.json();
                
                if (verifyData.ok) {
                    alert(verifyData.message || 'Supporter status activated!');
                    updatePatreonUI(true);
                } else {
                    alert(verifyData.message || 'Invalid supporter code. Please check your code and try again.');
                }
            }
        }
    });
    
    function updatePatreonUI(isSupporter) {
        const btn = document.getElementById('toggle_patreon_btn');
        btn.className = isSupporter ? 'btn-on' : 'btn-off';
        btn.textContent = `Patreon Supporter: ${isSupporter ? 'YES' : 'NO'}`;
        
        const premiumSection = document.getElementById('premium_styling_section');
        if (isSupporter) {
            premiumSection.style.opacity = '1';
            premiumSection.style.pointerEvents = 'auto';
            premiumSection.querySelectorAll('input, button').forEach(el => el.disabled = false);
        } else {
            premiumSection.style.opacity = '0.5';
            premiumSection.style.pointerEvents = 'none';
            premiumSection.querySelectorAll('input, button').forEach(el => el.disabled = true);
        }
    }
    
    document.getElementById('save_premium_styling_btn').addEventListener('click', async () => {
        const customBackground = document.getElementById('custom_background').value;
        const customButtonColor = document.getElementById('custom_button_color').value;
        
        const response = await fetch('/save_premium_styling', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                custom_background: customBackground,
                custom_button_color: customButtonColor
            })
        });
        
        if (response.ok) {
            applyPremiumStyling(customBackground, customButtonColor);
            alert('Premium styling saved successfully!');
        } else {
            alert('Error: You must be a Patreon supporter to use this feature.');
        }
    });
    
    document.getElementById('toggle_heart_rate_enabled_btn')?.addEventListener('click', async () => {
        const response = await fetch('/toggle_heart_rate_enabled', { method: 'POST' });
        const data = await response.json();
        const btn = document.getElementById('toggle_heart_rate_enabled_btn');
        btn.className = data.heart_rate_enabled ? 'btn-on' : 'btn-off';
        btn.textContent = `Heart Rate Tracking: ${data.heart_rate_enabled ? 'ON' : 'OFF'}`;
    });
    
    document.getElementById('heart_rate_source')?.addEventListener('change', (e) => {
        const source = e.target.value;
        document.getElementById('pulsoid_settings').style.display = source === 'pulsoid' ? 'block' : 'none';
        document.getElementById('hyperate_settings').style.display = source === 'hyperate' ? 'block' : 'none';
        document.getElementById('custom_api_settings').style.display = source === 'custom' ? 'block' : 'none';
    });
    
    document.getElementById('save_heart_rate_settings_btn')?.addEventListener('click', async () => {
        const source = document.getElementById('heart_rate_source').value;
        const pulsoidToken = document.getElementById('heart_rate_pulsoid_token').value;
        const hyperateId = document.getElementById('heart_rate_hyperate_id').value;
        const customApi = document.getElementById('heart_rate_custom_api').value;
        const updateInterval = document.getElementById('heart_rate_update_interval').value;
        
        await fetch('/save_heart_rate_settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                source,
                pulsoid_token: pulsoidToken,
                hyperate_id: hyperateId,
                custom_api: customApi,
                update_interval: updateInterval
            })
        });
        alert('Heart rate settings saved successfully!');
    });
    
    document.getElementById('generate_ai_btn')?.addEventListener('click', async () => {
        const mood = document.getElementById('ai_mood').value;
        const theme = document.getElementById('ai_theme').value;
        
        try {
            const response = await fetch('/generate_ai_message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mood, theme, max_length: 30 })
            });
            
            const data = await response.json();
            
            if (data.ok && data.message) {
                document.getElementById('ai_message_text').textContent = data.message;
                document.getElementById('ai_result').style.display = 'block';
                document.getElementById('ai_result').dataset.message = data.message;
            } else {
                alert(data.error || 'Failed to generate message. Make sure OPENAI_API_KEY is set.');
            }
        } catch (error) {
            alert('Error: ' + error.message);
        }
    });
    
    document.getElementById('add_ai_message_btn')?.addEventListener('click', async () => {
        const message = document.getElementById('ai_result').dataset.message;
        if (message) {
            await fetch('/add_custom_message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: message })
            });
            loadCustomMessages();
            document.getElementById('ai_result').style.display = 'none';
            alert('Message added to custom messages!');
        }
    });
    
    document.getElementById('check_updates_btn')?.addEventListener('click', async () => {
        try {
            const response = await fetch('/update_info');
            const data = await response.json();
            
            document.getElementById('current_version').textContent = data.current_version;
            
            if (data.update_info && data.update_info.update_available) {
                const info = data.update_info;
                document.getElementById('latest_version').textContent = info.latest_version;
                document.getElementById('release_name').textContent = info.release_name;
                document.getElementById('release_notes').textContent = info.release_notes.substring(0, 200) + '...';
                document.getElementById('release_link').href = info.release_url;
                document.getElementById('update_info').style.display = 'block';
                document.getElementById('no_update_info').style.display = 'none';
            } else {
                document.getElementById('update_info').style.display = 'none';
                document.getElementById('no_update_info').style.display = 'block';
            }
        } catch (error) {
            alert('Error checking for updates: ' + error.message);
        }
    });
    
    loadProfiles();
    
    document.getElementById('save_profile_btn')?.addEventListener('click', async () => {
        const name = prompt('Enter profile name:');
        if (name && name.trim()) {
            try {
                const response = await fetch('/save_profile', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: name.trim() })
                });
                const data = await response.json();
                if (data.ok) {
                    alert(data.message || 'Profile saved!');
                    loadProfiles();
                } else {
                    alert(data.error || 'Failed to save profile');
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }
    });
    
    document.getElementById('load_profile_btn')?.addEventListener('click', async () => {
        const select = document.getElementById('profile_select');
        const name = select.value;
        if (name) {
            try {
                const response = await fetch('/load_profile', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name })
                });
                const data = await response.json();
                if (data.ok) {
                    alert('Profile loaded! Reloading page...');
                    location.reload();
                } else {
                    alert(data.error || 'Failed to load profile');
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        } else {
            alert('Please select a profile first');
        }
    });
    
    document.getElementById('delete_profile_btn')?.addEventListener('click', async () => {
        const select = document.getElementById('profile_select');
        const name = select.value;
        if (name) {
            if (confirm(`Delete profile "${name}"?`)) {
                try {
                    const response = await fetch('/delete_profile', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name })
                    });
                    const data = await response.json();
                    if (data.ok) {
                        alert('Profile deleted!');
                        loadProfiles();
                    } else {
                        alert(data.error || 'Failed to delete profile');
                    }
                } catch (error) {
                    alert('Error: ' + error.message);
                }
            }
        } else {
            alert('Please select a profile first');
        }
    });
    
    document.getElementById('text_effect_select')?.addEventListener('change', async (e) => {
        const effect = e.target.value;
        try {
            await fetch('/set_text_effect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ effect })
            });
        } catch (error) {
            console.error('Error setting text effect:', error);
        }
    });
    
    document.getElementById('toggle_discord_btn')?.addEventListener('click', async () => {
        try {
            const response = await fetch('/toggle_discord', { method: 'POST' });
            const data = await response.json();
            const btn = document.getElementById('toggle_discord_btn');
            btn.className = data.discord_enabled ? 'btn-on' : 'btn-off';
            btn.textContent = `Discord Integration: ${data.discord_enabled ? 'ON' : 'OFF'}`;
        } catch (error) {
            console.error('Error toggling Discord:', error);
        }
    });
    
    document.getElementById('save_weather_location_btn')?.addEventListener('click', async () => {
        const location = document.getElementById('weather_location').value;
        try {
            await fetch('/save_weather_settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ location })
            });
            alert('Weather location saved!');
        } catch (error) {
            alert('Error: ' + error.message);
        }
    });
    
    updateDisplayOptionButtons();
    updateAdvancedButtons();
    updateMessageWeightsVisibility();
}

async function loadProfiles() {
    try {
        const response = await fetch('/profiles');
        const data = await response.json();
        const select = document.getElementById('profile_select');
        
        if (select) {
            select.innerHTML = '<option value="">-- Select a profile --</option>';
            data.profiles.forEach(profile => {
                const option = document.createElement('option');
                option.value = profile;
                option.textContent = profile;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading profiles:', error);
    }
}

async function updateAdvancedButtons() {
    try {
        const response = await fetch('/status');
        const data = await response.json();
        
        const randomOrderBtn = document.getElementById('random_order_btn');
        const showIconsBtn = document.getElementById('show_module_icons_btn');
        
        if (randomOrderBtn) {
            randomOrderBtn.className = data.random_order ? 'btn-on' : 'btn-off';
            randomOrderBtn.textContent = `Random Order: ${data.random_order ? 'ON' : 'OFF'}`;
        }
        
        if (showIconsBtn) {
            showIconsBtn.className = data.show_module_icons ? 'btn-on' : 'btn-off';
            showIconsBtn.textContent = `Module Icons: ${data.show_module_icons ? 'ON' : 'OFF'}`;
        }
    } catch (error) {
        console.error('Error updating advanced buttons:', error);
    }
}

async function updateMessageWeightsVisibility() {
    try {
        const response = await fetch('/status');
        const data = await response.json();
        const weightsSection = document.getElementById('message_weights_section');
        
        if (weightsSection) {
            weightsSection.style.display = data.random_order ? 'block' : 'none';
        }
    } catch (error) {
        console.error('Error updating weights visibility:', error);
    }
}

function setupProgressStyle() {
    const select = document.getElementById('select_progress_style');
    select.addEventListener('change', async () => {
        try {
            await fetch('/set_progress_style', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ style: select.value })
            });
        } catch (error) {
            console.error('Error setting progress style:', error);
        }
    });
}

async function loadCustomMessages() {
    try {
        const response = await fetch('/status');
        const data = await response.json();
        customMessages = data.custom_texts || [];
        renderInlineMessages();
    } catch (error) {
        console.error('Error loading custom messages:', error);
    }
}

function renderInlineMessages() {
    const container = document.getElementById('inline_messages_container');
    if (!container) return;
    
    container.innerHTML = '';
    
    customMessages.forEach((msg, idx) => {
        const div = document.createElement('div');
        div.style.cssText = 'display:flex;gap:8px;margin-bottom:8px;align-items:center;';
        
        const num = document.createElement('span');
        num.textContent = `${idx + 1}.`;
        num.style.cssText = 'min-width:30px;color:#0af;font-weight:700;';
        
        const upBtn = document.createElement('button');
        upBtn.textContent = '▲';
        upBtn.className = 'btn-on';
        upBtn.style.cssText = 'padding:4px 10px;font-size:10px;';
        upBtn.disabled = idx === 0;
        if (idx === 0) upBtn.style.opacity = '0.3';
        upBtn.addEventListener('click', () => moveMessage(idx, 'up'));
        
        const downBtn = document.createElement('button');
        downBtn.textContent = '▼';
        downBtn.className = 'btn-on';
        downBtn.style.cssText = 'padding:4px 10px;font-size:10px;';
        downBtn.disabled = idx === customMessages.length - 1;
        if (idx === customMessages.length - 1) downBtn.style.opacity = '0.3';
        downBtn.addEventListener('click', () => moveMessage(idx, 'down'));
        
        const input = document.createElement('input');
        input.type = 'text';
        input.value = msg;
        input.style.cssText = 'flex:1;';
        input.addEventListener('blur', () => updateMessage(idx, input.value));
        
        const deleteBtn = document.createElement('button');
        deleteBtn.textContent = '🗑';
        deleteBtn.className = 'btn-off';
        deleteBtn.style.cssText = 'padding:4px 8px;';
        deleteBtn.addEventListener('click', () => deleteMessage(idx));
        
        div.appendChild(num);
        div.appendChild(upBtn);
        div.appendChild(downBtn);
        div.appendChild(input);
        div.appendChild(deleteBtn);
        container.appendChild(div);
    });
}

async function updateMessage(index, text) {
    try {
        await fetch('/update_custom_inline', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ index, text })
        });
    } catch (error) {
        console.error('Error updating message:', error);
    }
}

async function deleteMessage(index) {
    try {
        await fetch('/delete_custom_message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ index })
        });
        loadCustomMessages();
        loadPerMessageTimings();
        loadMessageWeights();
    } catch (error) {
        console.error('Error deleting message:', error);
    }
}

async function moveMessage(index, direction) {
    try {
        await fetch('/move_custom_message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ index, direction })
        });
        loadCustomMessages();
        loadPerMessageTimings();
        loadMessageWeights();
    } catch (error) {
        console.error('Error moving message:', error);
    }
}

async function loadPerMessageTimings() {
    const container = document.getElementById('per_message_timing_container');
    if (!container) return;
    
    try {
        const response = await fetch('/status');
        const data = await response.json();
        customMessages = data.custom_texts || [];
        const savedIntervals = data.per_message_intervals || {};
        
        container.innerHTML = '';
        
        customMessages.forEach((msg, idx) => {
            const div = document.createElement('div');
            div.style.cssText = 'display:flex;gap:8px;margin-bottom:6px;align-items:center;';
            
            const label = document.createElement('label');
            label.textContent = `Msg ${idx + 1}: ${msg.substring(0, 30)}${msg.length > 30 ? '...' : ''}`;
            label.style.cssText = 'flex:1;';
            
            const input = document.createElement('input');
            input.type = 'number';
            input.min = '1';
            input.value = savedIntervals[String(idx)] || '3';
            input.style.cssText = 'width:80px;';
            input.addEventListener('change', () => savePerMessageTimings());
            input.dataset.index = idx;
            
            div.appendChild(label);
            div.appendChild(input);
            container.appendChild(div);
        });
    } catch (error) {
        console.error('Error loading per-message timings:', error);
    }
}

async function savePerMessageTimings() {
    const inputs = document.querySelectorAll('#per_message_timing_container input');
    const intervals = {};
    inputs.forEach(input => {
        intervals[input.dataset.index] = parseInt(input.value) || 3;
    });
    
    try {
        await fetch('/save_per_message_intervals', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ intervals })
        });
    } catch (error) {
        console.error('Error saving timings:', error);
    }
}

async function loadMessageWeights() {
    const container = document.getElementById('message_weights_container');
    if (!container) return;
    
    try {
        const response = await fetch('/status');
        const data = await response.json();
        customMessages = data.custom_texts || [];
        const savedWeights = data.weighted_messages || {};
        
        container.innerHTML = '';
        
        customMessages.forEach((msg, idx) => {
            const div = document.createElement('div');
            div.style.cssText = 'display:flex;gap:8px;margin-bottom:6px;align-items:center;';
            
            const label = document.createElement('label');
            label.textContent = `Msg ${idx + 1}: ${msg.substring(0, 30)}${msg.length > 30 ? '...' : ''}`;
            label.style.cssText = 'flex:1;';
            
            const input = document.createElement('input');
            input.type = 'number';
            input.min = '1';
            input.value = savedWeights[String(idx)] || '1';
            input.style.cssText = 'width:80px;';
            input.dataset.index = idx;
            input.addEventListener('change', async () => {
                await fetch('/set_message_weight', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        index: parseInt(input.dataset.index), 
                        weight: parseInt(input.value) 
                    })
                });
            });
            
            div.appendChild(label);
            div.appendChild(input);
            container.appendChild(div);
        });
    } catch (error) {
        console.error('Error loading message weights:', error);
    }
}

async function toggleChatbox() {
    try {
        await fetch('/toggle_chatbox', { method: 'POST' });
        await updateStatus();
    } catch (error) {
        console.error('Error:', error);
    }
}

async function toggleTime() {
    try {
        await fetch('/toggle_time', { method: 'POST' });
        await updateStatus();
    } catch (error) {
        console.error('Error:', error);
    }
}

async function toggleCustom() {
    try {
        await fetch('/toggle_custom', { method: 'POST' });
        await updateStatus();
    } catch (error) {
        console.error('Error:', error);
    }
}

async function toggleMusic() {
    try {
        await fetch('/toggle_music', { method: 'POST' });
        await updateStatus();
    } catch (error) {
        console.error('Error:', error);
    }
}

async function toggleMusicProgress() {
    try {
        await fetch('/toggle_music_progress', { method: 'POST' });
        await updateStatus();
    } catch (error) {
        console.error('Error:', error);
    }
}

async function toggleWindow() {
    try {
        await fetch('/toggle_window', { method: 'POST' });
        await updateStatus();
    } catch (error) {
        console.error('Error:', error);
    }
}

async function toggleHeartRate() {
    try {
        await fetch('/toggle_heartrate', { method: 'POST' });
        await updateStatus();
    } catch (error) {
        console.error('Error:', error);
    }
}

async function toggleWeather() {
    try {
        await fetch('/toggle_weather', { method: 'POST' });
        await updateStatus();
    } catch (error) {
        console.error('Error:', error);
    }
}

function applyPremiumStyling(customBackground, customButtonColor) {
    if (customBackground) {
        if (customBackground.startsWith('http') || customBackground.startsWith('https')) {
            document.body.style.backgroundImage = `url(${customBackground})`;
            document.body.style.backgroundSize = 'cover';
            document.body.style.backgroundPosition = 'center';
        } else if (customBackground.startsWith('#')) {
            document.body.style.backgroundColor = customBackground;
            document.body.style.backgroundImage = 'none';
        }
    }
    
    if (customButtonColor && customButtonColor.startsWith('#')) {
        const btnOns = document.querySelectorAll('.btn-on');
        btnOns.forEach(btn => {
            btn.style.background = `linear-gradient(135deg, ${customButtonColor}, ${customButtonColor}dd)`;
        });
    }
}

async function updateStatus() {
    try {
        const response = await fetch('/status');
        const data = await response.json();
        
        document.getElementById('chatbox_status').textContent = data.chatbox ? 'ON' : 'OFF';
        document.getElementById('time_status').textContent = data.time_on ? data.time : 'OFF';
        document.getElementById('custom_status').textContent = data.custom_on ? data.custom : 'OFF';
        document.getElementById('song_status').textContent = data.music_on ? data.song : 'OFF';
        document.getElementById('window_status').textContent = data.window_on ? data.window : 'OFF';
        document.getElementById('heartrate_status').textContent = data.heartrate_on ? data.heartrate : 'OFF';
        document.getElementById('weather_status').textContent = data.weather_on ? data.weather : 'OFF';
        document.getElementById('last_msg').textContent = data.last_message || '---';
        document.getElementById('preview').textContent = data.preview || 'Preview will show here.';
        
        const albumArt = document.getElementById('album_art');
        if (data.album_art) {
            albumArt.src = data.album_art;
        } else {
            albumArt.src = '';
        }
        
        const queueContainer = document.getElementById('message_queue');
        if (queueContainer && data.message_queue) {
            queueContainer.innerHTML = '';
            data.message_queue.forEach((msg, idx) => {
                const item = document.createElement('div');
                item.textContent = `${idx + 1}. ${msg}`;
                queueContainer.appendChild(item);
            });
        }
        
        updateButton('btn_chatbox', data.chatbox);
        updateButton('btn_time', data.time_on);
        updateButton('btn_custom', data.custom_on);
        updateButton('btn_music', data.music_on);
        updateButton('btn_window', data.window_on);
        updateButton('btn_heartrate', data.heartrate_on);
        updateButton('btn_weather', data.weather_on);
        updateButton('btn_music_progress', data.music_progress);
        
        if (data.theme) {
            let classes = [];
            if (data.theme === 'light') classes.push('light');
            if (data.compact_mode) classes.push('compact');
            document.body.className = classes.join(' ');
        }
        
        updateDisplayOptionButtons();
        
    } catch (error) {
        console.error('Error updating status:', error);
    }
}

async function updateDisplayOptionButtons() {
    try {
        const response = await fetch('/status');
        const data = await response.json();
        
        const themeBtn = document.getElementById('toggle_theme_btn');
        const streamerBtn = document.getElementById('toggle_streamer_btn');
        const compactBtn = document.getElementById('toggle_compact_btn');
        
        if (themeBtn) {
            themeBtn.className = data.theme === 'light' ? 'btn-on' : 'btn-off';
            themeBtn.textContent = `Theme: ${data.theme === 'light' ? 'Light' : 'Dark'}`;
        }
        
        if (streamerBtn) {
            streamerBtn.className = data.streamer_mode ? 'btn-on' : 'btn-off';
            streamerBtn.textContent = `Streamer Mode: ${data.streamer_mode ? 'ON' : 'OFF'}`;
        }
        
        if (compactBtn) {
            compactBtn.className = data.compact_mode ? 'btn-on' : 'btn-off';
            compactBtn.textContent = `Compact Mode: ${data.compact_mode ? 'ON' : 'OFF'}`;
        }
    } catch (error) {
        console.error('Error updating display buttons:', error);
    }
}

function updateButton(id, isOn) {
    const btn = document.getElementById(id);
    if (btn) {
        btn.className = isOn ? 'btn-on' : 'btn-off';
    }
}

function startUpdate() {
    updateStatus();
    if (updateTimer) clearInterval(updateTimer);
    updateTimer = setInterval(updateStatus, refreshInterval * 1000);
}

function setupLayout() {
    const list = document.getElementById('layout_list');
    let draggedItem = null;

    list.addEventListener('dragstart', (e) => {
        draggedItem = e.target;
        e.target.style.opacity = '0.5';
    });

    list.addEventListener('dragend', (e) => {
        e.target.style.opacity = '1';
    });

    list.addEventListener('dragover', (e) => {
        e.preventDefault();
        const afterElement = getDragAfterElement(list, e.clientY);
        if (afterElement == null) {
            list.appendChild(draggedItem);
        } else {
            list.insertBefore(draggedItem, afterElement);
        }
    });

    list.addEventListener('drop', async (e) => {
        e.preventDefault();
        const items = Array.from(list.querySelectorAll('.layout-item'));
        const order = items.map(item => item.dataset.key);
        
        try {
            await fetch('/save_layout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ layout_order: order })
            });
        } catch (error) {
            console.error('Error saving layout:', error);
        }
    });
}

function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.layout-item:not(.dragging)')];
    
    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        
        if (offset < 0 && offset > closest.offset) {
            return { offset: offset, element: child };
        } else {
            return closest;
        }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
}

document.getElementById('manual_msg_form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    try {
        const response = await fetch('/send', {
            method: 'POST',
            body: formData
        });
        if (response.ok) {
            e.target.reset();
            await updateStatus();
        }
    } catch (error) {
        console.error('Error sending message:', error);
    }
});
