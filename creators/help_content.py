# creators/help_content.py
HELP_TOPICS = {
    'hs_code': {
        'title': 'HS Code｜海關商品編碼',
        'body': """
        <p>HS Code 是海關申報和計算關稅用的國際商品編碼，<strong>不確定可以留空</strong>，管理員會在審核時補填。</p>
        <p class="opacity-70">The Harmonized System code is used for customs declaration and duty calculation. Leave blank if unsure — an admin will fill it in during review.</p>
        <p class="mt-2">常見藝術品參考：</p>
        <ul class="list-disc list-inside text-[13px] opacity-80">
            <li><span class="font-mono">9701</span> — 繪畫、拼貼（Paintings, collages）</li>
            <li><span class="font-mono">9702</span> / <span class="font-mono">9703</span> — 原創雕塑、雕像（Original sculptures）</li>
            <li><span class="font-mono">9705</span> — 收藏品（Collectors' pieces）</li>
            <li><span class="font-mono">6913/6914</span> — 陶瓷器（Ceramics）</li>
            <li><span class="font-mono">4420</span> — 木製工藝品（Woodwork）</li>
            <li><span class="font-mono">6304</span> — 紡織成品（Textile articles）</li>
            <li><span class="font-mono">7117</span> — 首飾（Jewellery）</li>
        </ul>
        """,
    },
    'tags': {
        'title': 'Tags｜標籤',
        'body': """
        <p>標籤影響買家在站內搜索和主題頁中看到你的作品。請從現有標籤中挑選最貼切的 3–5 個。</p>
        <p class="opacity-70">Tags affect how buyers find your work in search and topic pages. Pick the 3–5 most relevant.</p>
        <p class="mt-2">找不到合適的標籤？<strong>聯繫平台後台</strong>申請新增，請提供中英文標籤名。</p>
        """,
    },
    'craft_types': {
        'title': 'Craft Types｜工藝類型 vs Category 分類',
        'body': """
        <p><strong>分類（Category）</strong>決定作品出現在店鋪的哪個貨架；<strong>工藝類型</strong>是橫向標記，用於匠人頁和主題策展（例如「所有金工作品」）。兩者可以重疊，不用糾結。</p>
        <p class="opacity-70">Category decides which shelf your piece sits on; craft types are cross-cutting labels used for curation. They may overlap — don't worry.</p>
        """,
    },
    'digital_fulfillment': {
        'title': 'Digital Fulfillment｜電子交付方式',
        'body': """
        <ul class="list-disc list-inside space-y-1">
            <li><strong>INSTANT｜即時交付</strong>：付款後買家立刻下載同一個檔案。庫存固定為 1。</li>
            <li><strong>CUSTOM / MANUAL｜人工交付</strong>：適合線上工作坊、訂製畫、約稿。每筆訂單你與買家個別交付，並在上傳 Vault 檔案後等待管理員審核。</li>
        </ul>
        <p class="mt-2 opacity-70">Files enter a review queue and go live only after admin approval. 檔案需經管理員審核後才會交付給買家。</p>
        """,
    },
    'rec_metadata': {
        'title': '推薦標籤（可選）',
        'body': """
        <p>這三個標籤只餵給平台的推薦系統，幫助把你的作品配對給更可能喜歡它的訪客，<strong>不影響搜索</strong>。</p>
        <p class="opacity-70">These tags only feed the recommendation engine; they don't affect search. Keep defaults if unsure.</p>
        <p class="mt-2">完全沒想法就保持預設（未指定/通用），不會有負面影響。</p>
        """,
    },
    'original_price': {
        'title': 'Original Price｜原價',
        'body': """
        <p>原價是「劃線價」，會和售價一起顯示（如 <s>¥1,200</s> ¥980），用於表達折扣。</p>
        <p class="opacity-70">The strike-through price shown next to your sale price. Leave blank if not running a discount.</p>
        <p class="mt-2">不建議長期虛高原價——平台活動疊加折扣時，差額由誰承擔會顯示在款式卡片上。</p>
        """,
    },
    'with_shipping': {
        'title': '含運費 vs 單件包裝',
        'body': """
        <ul class="list-disc list-inside space-y-1">
            <li><strong>含運費</strong>：運費已包在售價裡，買家免運。適合輕小、運費可預估的作品。</li>
            <li><strong>單件包裝</strong>：每件單獨計運費（如畫作不能合箱）。<strong>不勾選</strong> = 同一訂單多個款式可合併計運費，對買家更友好。</li>
        </ul>
        <p class="mt-2 opacity-70">Single Pack: each unit ships separately. Unchecked = units in one order can share shipping.</p>
        """,
    },
    'featured_image': {
        'title': '主視覺 Featured Image',
        'body': """
        <p>主視覺是作品在列表頁、搜索結果和社交分享中顯示的第一張圖，建議：</p>
        <ul class="list-disc list-inside text-[13px]">
            <li>4:3 比例，主體居中，背景乾淨</li>
            <li>光線均勻、無水印、無邊框</li>
            <li>選檔後可裁剪；預覽於儲存後更新</li>
        </ul>
        """,
    },
    'gallery': {
        'title': 'Gallery Images｜作品相簿',
        'body': """
        <p>上傳 1–5 張照片，顯示於商品頁輪播。建議組合：整體照、細節照、比例參照（手部或室內陳設）。</p>
        <p class="opacity-70">Upload 1–5 images shown in the product page carousel. A good set: overall, detail, and a scale reference.</p>
        """,
    },
}