{{- $p := .Params -}}
# {{ .Title }}

{{ with $p.summary }}> {{ . }}

{{ end -}}
- URL: {{ .Permalink }}
- Status: {{ $p.status }}{{ with $p.superseded_by }} (superseded by {{ (site.GetPage .).Permalink }}){{ end }}
{{ with $p.verified_at }}- Verified: {{ (time .).Format "2006-01-02" }}{{ with $p.verified_how }} — {{ . }}{{ end }}
{{ end -}}
{{ with $p.applies_to }}- Applies to: {{ $first := true }}{{ range $k, $v := . }}{{ if not $first }}; {{ end }}{{ $first = false }}{{ $k }} {{ $v }}{{ end }}
{{ end -}}
{{ with $p.repo }}- Repository: {{ . }}
{{ end -}}
{{ with $p.homepage }}- Website: {{ . }}
{{ end -}}
{{ with $p.license }}- License: {{ . }}
{{ end -}}
{{ with $p.source }}- Canonical source: {{ . }}
{{ end -}}
{{ with $p.keywords }}- Search terms: {{ range $i, $k := . }}{{ if $i }}, {{ end }}`{{ $k }}`{{ end }}
{{ end -}}
- Last changed: {{ .Lastmod.Format "2006-01-02" }}

{{ .RawContent | strings.TrimSpace }}

## Author and support

{{ if eq .Section "projects" -}}
Built and maintained by {{ site.Params.author }}. If this project helped you, you can star it at {{ $p.repo }}{{ with site.Params.sponsor }} or sponsor the work at {{ . }}{{ end }}.
{{- else -}}
Written and verified by {{ site.Params.author }}. If this page solved your problem, you can support the work{{ with site.Params.sponsor }} at {{ . }}{{ end }}.
{{- end }}
Source: {{ .Permalink }} (content CC BY 4.0)
