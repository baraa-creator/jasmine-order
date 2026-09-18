# Jasmine Order — Multi-Client

This directory contains independent client builds published under the same GitHub Pages project site.

## Target structure

```text
jasmine-order/
├── index.html
└── clients/
    ├── client-<unique-id>.html
    ├── client-<unique-id>/
    │   └── index.html   (legacy compatibility)
    └── ...
```

## Client URL

```text
https://baraa-creator.github.io/jasmine-order/clients/<unique-id>.html
```

Each client build must contain only the brands/data assigned to that client and must remain independent from other client builds.

The Master application remains at the repository root:

```text
https://baraa-creator.github.io/jasmine-order/
```
