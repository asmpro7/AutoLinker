
<h1>AutoLinker</h1>

<p>AutoLinker is a <strong>Telegram bot</strong> designed to automatically track new messages in channels, extract hashtags, and update an index message with hyperlinks to the new messages. It uses <strong>Pyrogram</strong> to interact with Telegram and <strong>SQLite</strong> as a local database. Airtable is used as a dashboard to manage the mapping of channels, subjects, topics, and index messages.</p>

<h2>Features</h2>
<ul>
  <li>Monitors multiple Telegram channels for new messages.</li>
  <li>Extracts hashtags in the format: <code>#Subject_Topic_Type</code></li>
  <li>Updates index messages in channels with hyperlinks to new messages.</li>
  <li>Preserves all previous links when adding new ones.</li>
  <li>Supports local SQLite database and optional Airtable synchronization.</li>
</ul>

<h2>Repository Structure</h2>
<pre>
AutoLinker/
├─ AutoLinker.py      # Main bot script
├─ autolinker.db      # SQLite database 
├─ requirements.txt   # Python dependencies
</pre>

<h2>Requirements</h2>
<ul>
  <li>Python >= 3.8</li>
  <li><a href="https://docs.kurigram.icu/">kurigram</a></li>
  <li><a href="https://pypi.org/project/pyairtable/">pyairtable</a></li>
</ul>

<h3>Install Requirements</h3>
<pre>
pip install -r requirements.txt
</pre>

<p><strong>requirements.txt</strong></p>
<pre>
pyrogram==2.2.7
tgcrypto
pyairtable
</pre>

<h2>Configuration</h2>

<h3>1. Telegram Bot</h3>
<ul>
  <li>Create a Telegram bot using <a href="https://t.me/BotFather">@BotFather</a> and get your <strong>bot token</strong>.</li>
  <li>Get your <strong>API ID</strong> and <strong>API hash</strong> from <a href="https://my.telegram.org">my.telegram.org</a>.</li>
</ul>

<h3>2. Bot Settings in AutoLinker.py</h3>
<pre>
api_id = 0000
api_hash = "000"
bot_token = "000:000"
SESSION_NAME = "autolinker"
</pre>

<h3>3. SQLite Database (<code>autolinker.db</code>)</h3>
<p>The local database stores the mapping of channels, subjects, topics, and index messages.</p>

<table border="1" cellpadding="5" cellspacing="0">
  <thead>
    <tr>
      <th>Column</th>
      <th>Type</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>channel_id</td>
      <td>INTEGER</td>
      <td>Normalized Telegram channel ID (without -100 prefix)</td>
    </tr>
    <tr>
      <td>subject</td>
      <td>TEXT</td>
      <td>First category (e.g., Nephrology)</td>
    </tr>
    <tr>
      <td>topic</td>
      <td>TEXT</td>
      <td>Second category (e.g., Lec1)</td>
    </tr>
    <tr>
      <td>message_id</td>
      <td>INTEGER</td>
      <td>Telegram message ID of the index message (manually added)</td>
    </tr>
  </tbody>
</table>

<p><strong>Example row:</strong></p>
<pre>
| channel_id | subject     | topic  | message_id |
|------------|-------------|--------|------------|
| 3027270206 | Nephrology | Lec1   | 413         |
</pre>

<h3>4. Airtable Settings in AutoLinker.py</h3>
<pre>
AIRTABLE_API_KEY = "000.000"
AIRTABLE_BASE_ID = "app000"
AIRTABLE_TABLE_NAME = "AutoLinker"
</pre>
<ul>
  <li>Create a table in Airtable with columns identical to the SQLite database: <code>channel_id</code>, <code>subject</code>, <code>topic</code>, <code>message_id</code>.</li>
  
  
  <li>Use the <code>/update</code> command in the bot to synchronize Airtable with the local database.</li>
</ul>

<h2>Usage</h2>

<ol>
  <li>Start the bot:
  <pre>python AutoLinker.py</pre>
  </li>
  <li>Commands:
    <ul>
      <li><code>/update</code> — Sync local database with Airtable.</li>
    </ul>
  </li>
  <li>Message Listener:
    <ul>
      <li>The bot automatically listens to channels.</li>
      <li>When a new message contains a hashtag like <code>#Nephrology_Lec1_courses</code>, the bot:
        <ul>
          <li>Finds the corresponding index message from the database.</li>
          <li>Inserts a new hyperlink under the type (<code>courses</code>) preserving old links.</li>
          <li>The hyperlink uses the second line of the new message as the link text.</li>
        </ul>
      </li>
    </ul>
  </li>
</ol>


<h2>License</h2>
<p>This project is licensed under the <strong>MIT License</strong>.</p>

</body>
