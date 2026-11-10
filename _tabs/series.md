---
# 파트별 글을 읽는 순서대로 보여 준다. 글의 front matter에 series와 series_order가 있어야 나온다.
title: 시리즈
icon: fas fa-list-ol
order: 1
---

센서에서 데이터 저장까지 센서 시스템을 만드는 순서대로 다섯 파트, 그리고 실제로 쓰는 장비 파트로 묶었습니다.

{% assign parts = site.data.series %}
{% for part in parts %}
{% assign items = site.posts | where: "series", part.key | sort: "series_order" %}
## {{ part.title }}

{{ part.summary }}

{% if items.size > 0 %}
{% for p in items %}
{{ forloop.index }}. [{{ p.title }}]({{ p.url | relative_url }})
{% endfor %}
{% else %}
_준비 중입니다._
{% endif %}
{% endfor %}
