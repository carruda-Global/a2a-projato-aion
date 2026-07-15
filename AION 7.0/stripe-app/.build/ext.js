"use strict";
var __StripeExtExports = (() => {
  var __create = Object.create;
  var __defProp = Object.defineProperty;
  var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
  var __getOwnPropNames = Object.getOwnPropertyNames;
  var __getProtoOf = Object.getPrototypeOf;
  var __hasOwnProp = Object.prototype.hasOwnProperty;
  var __require = /* @__PURE__ */ ((x) => typeof require !== "undefined" ? require : typeof Proxy !== "undefined" ? new Proxy(x, {
    get: (a, b) => (typeof require !== "undefined" ? require : a)[b]
  }) : x)(function(x) {
    if (typeof require !== "undefined")
      return require.apply(this, arguments);
    throw new Error('Dynamic require of "' + x + '" is not supported');
  });
  var __commonJS = (cb, mod) => function __require2() {
    return mod || (0, cb[__getOwnPropNames(cb)[0]])((mod = { exports: {} }).exports, mod), mod.exports;
  };
  var __export = (target, all) => {
    for (var name in all)
      __defProp(target, name, { get: all[name], enumerable: true });
  };
  var __copyProps = (to, from, except, desc) => {
    if (from && typeof from === "object" || typeof from === "function") {
      for (let key of __getOwnPropNames(from))
        if (!__hasOwnProp.call(to, key) && key !== except)
          __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
    }
    return to;
  };
  var __reExport = (target, mod, secondTarget) => (__copyProps(target, mod, "default"), secondTarget && __copyProps(secondTarget, mod, "default"));
  var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(
    isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target,
    mod
  ));
  var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

  // node_modules/@stripe/ui-extension-sdk/version.js
  var require_version = __commonJS({
    "node_modules/@stripe/ui-extension-sdk/version.js"(exports) {
      "use strict";
      Object.defineProperty(exports, "__esModule", { value: true });
      exports.SDK_VERSION = void 0;
      exports.SDK_VERSION = "9.1.0";
    }
  });

  // node_modules/@stripe/ui-extension-sdk/ui/index.js
  var require_ui = __commonJS({
    "node_modules/@stripe/ui-extension-sdk/ui/index.js"(exports) {
      "use strict";
      Object.defineProperty(exports, "__esModule", { value: true });
      exports.TableHeaderCell = exports.TableHead = exports.TableFooter = exports.TableCell = exports.TableBody = exports.Tab = exports.TabPanels = exports.TabPanel = exports.TabList = exports.Switch = exports.StripeFileUploader = exports.Spinner = exports.Sparkline = exports.SignInView = exports.SettingsView = exports.Select = exports.Radio = exports.PropertyList = exports.PropertyListItem = exports.PlatformConfigurationView = exports.OnboardingView = exports.Menu = exports.MenuItem = exports.MenuGroup = exports.List = exports.ListItem = exports.Link = exports.LineChart = exports.Inline = exports.Img = exports.Icon = exports.FormFieldGroup = exports.FocusView = exports.Divider = exports.DetailPageTable = exports.DetailPagePropertyList = exports.DetailPageModule = exports.DateField = exports.ContextView = exports.Chip = exports.ChipList = exports.Checkbox = exports.Button = exports.ButtonGroup = exports.Box = exports.BarChart = exports.Banner = exports.Badge = exports.Accordion = exports.AccordionItem = void 0;
      exports.Tooltip = exports.TextField = exports.TextArea = exports.TaskList = exports.TaskListItem = exports.Tabs = exports.TableRow = exports.Table = void 0;
      var jsx_runtime_1 = __require("react/jsx-runtime");
      var react_1 = __require("@remote-ui/react");
      var version_1 = require_version();
      var withSdkProps = (Component) => {
        const wrappedComponentName = Component.displayName || Component.toString();
        const WithSdkProps = (props) => (0, jsx_runtime_1.jsx)(Component, { ...props, wrappedComponentName, sdkVersion: version_1.SDK_VERSION, schemaVersion: "v9" });
        WithSdkProps.wrappedComponentName = wrappedComponentName;
        return WithSdkProps;
      };
      var defineComponent = (name, fragmentProps, wrapWithSdkProps) => {
        const remoteComponent = (0, react_1.createRemoteReactComponent)(name, {
          fragmentProps
        });
        if (!wrapWithSdkProps) {
          return remoteComponent;
        }
        return withSdkProps(remoteComponent);
      };
      exports.AccordionItem = defineComponent("AccordionItem", ["title", "actions", "media", "subtitle"], true);
      exports.Accordion = defineComponent("Accordion", [], true);
      exports.Badge = defineComponent("Badge", [], true);
      exports.Banner = defineComponent("Banner", ["actions", "description", "title"], true);
      exports.BarChart = defineComponent("BarChart", [], true);
      exports.Box = defineComponent("Box", [], true);
      exports.ButtonGroup = defineComponent("ButtonGroup", ["menuTrigger"], true);
      exports.Button = defineComponent("Button", [], true);
      exports.Checkbox = defineComponent("Checkbox", ["label"], true);
      exports.ChipList = defineComponent("ChipList", [], true);
      exports.Chip = defineComponent("Chip", [], true);
      exports.ContextView = defineComponent("ContextView", ["actions", "banner", "footerContent", "primaryAction", "secondaryAction"], true);
      exports.DateField = defineComponent("DateField", ["label"], true);
      exports.DetailPageModule = defineComponent("DetailPageModule", [], true);
      exports.DetailPagePropertyList = defineComponent("DetailPagePropertyList", [], true);
      exports.DetailPageTable = defineComponent("DetailPageTable", [], true);
      exports.Divider = defineComponent("Divider", [], true);
      exports.FocusView = defineComponent("FocusView", ["footerContent", "primaryAction", "secondaryAction"], true);
      exports.FormFieldGroup = defineComponent("FormFieldGroup", [], true);
      exports.Icon = defineComponent("Icon", [], true);
      exports.Img = defineComponent("Img", [], true);
      exports.Inline = defineComponent("Inline", [], true);
      exports.LineChart = defineComponent("LineChart", [], true);
      exports.Link = defineComponent("Link", [], true);
      exports.ListItem = defineComponent("ListItem", ["icon", "image", "secondaryTitle", "title", "value"], true);
      exports.List = defineComponent("List", [], true);
      exports.MenuGroup = defineComponent("MenuGroup", ["title"], true);
      exports.MenuItem = defineComponent("MenuItem", [], true);
      exports.Menu = defineComponent("Menu", ["trigger"], true);
      exports.OnboardingView = defineComponent("OnboardingView", ["error"], true);
      exports.PlatformConfigurationView = defineComponent("PlatformConfigurationView", [], true);
      exports.PropertyListItem = defineComponent("PropertyListItem", ["label", "value"], true);
      exports.PropertyList = defineComponent("PropertyList", [], true);
      exports.Radio = defineComponent("Radio", ["label"], true);
      exports.Select = defineComponent("Select", ["label"], true);
      exports.SettingsView = defineComponent("SettingsView", [], true);
      exports.SignInView = defineComponent("SignInView", ["descriptionActionContents", "footerContent"], true);
      exports.Sparkline = defineComponent("Sparkline", [], true);
      exports.Spinner = defineComponent("Spinner", [], true);
      exports.StripeFileUploader = defineComponent("StripeFileUploader", [], true);
      exports.Switch = defineComponent("Switch", ["label"], true);
      exports.TabList = defineComponent("TabList", [], true);
      exports.TabPanel = defineComponent("TabPanel", [], true);
      exports.TabPanels = defineComponent("TabPanels", [], true);
      exports.Tab = defineComponent("Tab", [], true);
      exports.TableBody = defineComponent("TableBody", [], true);
      exports.TableCell = defineComponent("TableCell", [], true);
      exports.TableFooter = defineComponent("TableFooter", [], true);
      exports.TableHead = defineComponent("TableHead", [], true);
      exports.TableHeaderCell = defineComponent("TableHeaderCell", [], true);
      exports.Table = defineComponent("Table", [], true);
      exports.TableRow = defineComponent("TableRow", [], true);
      exports.Tabs = defineComponent("Tabs", [], true);
      exports.TaskListItem = defineComponent("TaskListItem", [], true);
      exports.TaskList = defineComponent("TaskList", [], true);
      exports.TextArea = defineComponent("TextArea", ["label"], true);
      exports.TextField = defineComponent("TextField", ["label"], true);
      exports.Tooltip = defineComponent("Tooltip", ["trigger"], true);
    }
  });

  // .build/manifest.js
  var manifest_exports = {};
  __export(manifest_exports, {
    AppView: () => AppView_default,
    BUILD_TIME: () => BUILD_TIME,
    default: () => manifest_default
  });

  // src/views/AppView.tsx
  var import_ui = __toESM(require_ui());
  var import_react = __require("react");
  var import_jsx_runtime = __require("react/jsx-runtime");
  var API_URL = "https://engenheiro-producao-ai.onrender.com";
  var EcosystemApp = ({ userContext }) => {
    const [score, setScore] = (0, import_react.useState)(null);
    const [loading, setLoading] = (0, import_react.useState)(true);
    const [error, setError] = (0, import_react.useState)(null);
    (0, import_react.useEffect)(() => {
      fetchComplianceScore();
    }, []);
    const fetchComplianceScore = async () => {
      try {
        const response = await fetch(`${API_URL}/api/stripe/compliance-score`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ stripe_account_id: userContext?.account?.id, email: userContext?.account?.email })
        });
        const data = await response.json();
        setScore(data);
      } catch {
        setError("N\xE3o foi poss\xEDvel carregar o score.");
      } finally {
        setLoading(false);
      }
    };
    const getScoreColor = (s) => s >= 80 ? "success" : s >= 50 ? "warning" : "critical";
    if (loading)
      return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(import_ui.ContextView, {
        title: "EcoSystem Compliance",
        children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_ui.Box, {
          css: { stack: "x", gap: "medium", alignY: "center" },
          children: [
            /* @__PURE__ */ (0, import_jsx_runtime.jsx)(import_ui.Spinner, {}),
            /* @__PURE__ */ (0, import_jsx_runtime.jsx)(import_ui.Text, {
              children: "Analisando compliance da sua empresa..."
            })
          ]
        })
      });
    if (error)
      return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(import_ui.ContextView, {
        title: "EcoSystem Compliance",
        children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(import_ui.Banner, {
          type: "critical",
          title: "Erro",
          description: error
        })
      });
    return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_ui.ContextView, {
      title: "EcoSystem Compliance",
      description: "Score de compliance regulat\xF3rio da sua empresa",
      children: [
        /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_ui.Box, {
          css: { padding: "large", background: "container", borderRadius: "medium", marginBottom: "medium" },
          children: [
            /* @__PURE__ */ (0, import_jsx_runtime.jsx)(import_ui.Text, {
              size: "small",
              color: "secondary",
              children: "Score de Compliance"
            }),
            /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_ui.Box, {
              css: { stack: "x", alignY: "center", gap: "small", marginTop: "small" },
              children: [
                /* @__PURE__ */ (0, import_jsx_runtime.jsx)(import_ui.Text, {
                  size: "xxlarge",
                  weight: "bold",
                  color: getScoreColor(score?.score || 0),
                  children: score?.score || 0
                }),
                /* @__PURE__ */ (0, import_jsx_runtime.jsx)(import_ui.Text, {
                  size: "xlarge",
                  color: "secondary",
                  children: "/100"
                }),
                /* @__PURE__ */ (0, import_jsx_runtime.jsx)(import_ui.Badge, {
                  type: getScoreColor(score?.score || 0),
                  children: score?.nivel
                })
              ]
            })
          ]
        }),
        /* @__PURE__ */ (0, import_jsx_runtime.jsx)(import_ui.Divider, {}),
        /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_ui.Box, {
          css: { marginTop: "medium", marginBottom: "medium" },
          children: [
            /* @__PURE__ */ (0, import_jsx_runtime.jsx)(import_ui.Text, {
              weight: "semibold",
              size: "small",
              children: "Obriga\xE7\xF5es Regulat\xF3rias"
            }),
            /* @__PURE__ */ (0, import_jsx_runtime.jsx)(import_ui.List, {
              children: score?.obrigacoes.map((ob, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(import_ui.ListItem, {
                title: ob.nome,
                value: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(import_ui.Badge, {
                  type: ob.status === "ok" ? "success" : "critical",
                  children: ob.status === "ok" ? "Em dia" : "Cr\xEDtico"
                })
              }, i))
            })
          ]
        }),
        /* @__PURE__ */ (0, import_jsx_runtime.jsx)(import_ui.Divider, {}),
        score?.score && score.score < 100 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_ui.Box, {
          css: { marginTop: "medium" },
          children: [
            /* @__PURE__ */ (0, import_jsx_runtime.jsx)(import_ui.Banner, {
              type: "warning",
              title: `Plano recomendado: ${score.plano_recomendado}`,
              description: "Regularize sua empresa em 48h com nossos agentes de IA"
            }),
            /* @__PURE__ */ (0, import_jsx_runtime.jsx)(import_ui.Box, {
              css: { marginTop: "small" },
              children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(import_ui.Button, {
                type: "primary",
                href: score.link_ativacao,
                target: "_blank",
                children: "Ativar agentes de compliance \u2192"
              })
            })
          ]
        }),
        /* @__PURE__ */ (0, import_jsx_runtime.jsx)(import_ui.Box, {
          css: { marginTop: "medium" },
          children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(import_ui.Text, {
            size: "xsmall",
            color: "secondary",
            children: "Powered by EcoSystem AI \u2014 Global Match Engenharia"
          })
        })
      ]
    });
  };
  var AppView_default = EcosystemApp;

  // .build/manifest.js
  __reExport(manifest_exports, __toESM(require_version()));
  var BUILD_TIME = "2026-06-26 21:20:46.6839212 -0300 -03 m=+3.319805501";
  var manifest_default = {
    "$schema": "https://stripe.com/stripe-app.schema.json",
    "distribution_type": "public",
    "icon": "./public/icon.png",
    "id": "com.globalengenharia.ecosystem-compliance",
    "name": "EcoSystem Compliance",
    "permissions": [
      {
        "permission": "customer_read",
        "purpose": "Identificar empresa para gerar score de compliance"
      },
      {
        "permission": "invoice_read",
        "purpose": "Verificar volume de transacoes para recomendar agentes"
      }
    ],
    "ui_extension": {
      "content_security_policy": {
        "connect-src": [
          "https://engenheiro-producao-ai.onrender.com/api/stripe/compliance-score"
        ],
        "purpose": "Conectar ao EcoSystem API para gerar score de compliance"
      },
      "views": [
        {
          "component": "AppView",
          "viewport": "stripe.dashboard.home.overview"
        }
      ]
    },
    "version": "1.0.0"
  };
  return __toCommonJS(manifest_exports);
})();
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsiLi4vbm9kZV9tb2R1bGVzL0BzdHJpcGUvdWktZXh0ZW5zaW9uLXNkay92ZXJzaW9uLmpzIiwgIi4uL25vZGVfbW9kdWxlcy9Ac3RyaXBlL3VpLWV4dGVuc2lvbi1zZGsvdWkvaW5kZXguanMiLCAibWFuaWZlc3QuanMiLCAiLi4vc3JjL3ZpZXdzL0FwcFZpZXcudHN4Il0sCiAgInNvdXJjZXNDb250ZW50IjogWyJcInVzZSBzdHJpY3RcIjtcbk9iamVjdC5kZWZpbmVQcm9wZXJ0eShleHBvcnRzLCBcIl9fZXNNb2R1bGVcIiwgeyB2YWx1ZTogdHJ1ZSB9KTtcbmV4cG9ydHMuU0RLX1ZFUlNJT04gPSB2b2lkIDA7XG5leHBvcnRzLlNES19WRVJTSU9OID0gJzkuMS4wJztcbiIsICJcInVzZSBzdHJpY3RcIjtcbk9iamVjdC5kZWZpbmVQcm9wZXJ0eShleHBvcnRzLCBcIl9fZXNNb2R1bGVcIiwgeyB2YWx1ZTogdHJ1ZSB9KTtcbmV4cG9ydHMuVGFibGVIZWFkZXJDZWxsID0gZXhwb3J0cy5UYWJsZUhlYWQgPSBleHBvcnRzLlRhYmxlRm9vdGVyID0gZXhwb3J0cy5UYWJsZUNlbGwgPSBleHBvcnRzLlRhYmxlQm9keSA9IGV4cG9ydHMuVGFiID0gZXhwb3J0cy5UYWJQYW5lbHMgPSBleHBvcnRzLlRhYlBhbmVsID0gZXhwb3J0cy5UYWJMaXN0ID0gZXhwb3J0cy5Td2l0Y2ggPSBleHBvcnRzLlN0cmlwZUZpbGVVcGxvYWRlciA9IGV4cG9ydHMuU3Bpbm5lciA9IGV4cG9ydHMuU3BhcmtsaW5lID0gZXhwb3J0cy5TaWduSW5WaWV3ID0gZXhwb3J0cy5TZXR0aW5nc1ZpZXcgPSBleHBvcnRzLlNlbGVjdCA9IGV4cG9ydHMuUmFkaW8gPSBleHBvcnRzLlByb3BlcnR5TGlzdCA9IGV4cG9ydHMuUHJvcGVydHlMaXN0SXRlbSA9IGV4cG9ydHMuUGxhdGZvcm1Db25maWd1cmF0aW9uVmlldyA9IGV4cG9ydHMuT25ib2FyZGluZ1ZpZXcgPSBleHBvcnRzLk1lbnUgPSBleHBvcnRzLk1lbnVJdGVtID0gZXhwb3J0cy5NZW51R3JvdXAgPSBleHBvcnRzLkxpc3QgPSBleHBvcnRzLkxpc3RJdGVtID0gZXhwb3J0cy5MaW5rID0gZXhwb3J0cy5MaW5lQ2hhcnQgPSBleHBvcnRzLklubGluZSA9IGV4cG9ydHMuSW1nID0gZXhwb3J0cy5JY29uID0gZXhwb3J0cy5Gb3JtRmllbGRHcm91cCA9IGV4cG9ydHMuRm9jdXNWaWV3ID0gZXhwb3J0cy5EaXZpZGVyID0gZXhwb3J0cy5EZXRhaWxQYWdlVGFibGUgPSBleHBvcnRzLkRldGFpbFBhZ2VQcm9wZXJ0eUxpc3QgPSBleHBvcnRzLkRldGFpbFBhZ2VNb2R1bGUgPSBleHBvcnRzLkRhdGVGaWVsZCA9IGV4cG9ydHMuQ29udGV4dFZpZXcgPSBleHBvcnRzLkNoaXAgPSBleHBvcnRzLkNoaXBMaXN0ID0gZXhwb3J0cy5DaGVja2JveCA9IGV4cG9ydHMuQnV0dG9uID0gZXhwb3J0cy5CdXR0b25Hcm91cCA9IGV4cG9ydHMuQm94ID0gZXhwb3J0cy5CYXJDaGFydCA9IGV4cG9ydHMuQmFubmVyID0gZXhwb3J0cy5CYWRnZSA9IGV4cG9ydHMuQWNjb3JkaW9uID0gZXhwb3J0cy5BY2NvcmRpb25JdGVtID0gdm9pZCAwO1xuZXhwb3J0cy5Ub29sdGlwID0gZXhwb3J0cy5UZXh0RmllbGQgPSBleHBvcnRzLlRleHRBcmVhID0gZXhwb3J0cy5UYXNrTGlzdCA9IGV4cG9ydHMuVGFza0xpc3RJdGVtID0gZXhwb3J0cy5UYWJzID0gZXhwb3J0cy5UYWJsZVJvdyA9IGV4cG9ydHMuVGFibGUgPSB2b2lkIDA7XG5jb25zdCBqc3hfcnVudGltZV8xID0gcmVxdWlyZShcInJlYWN0L2pzeC1ydW50aW1lXCIpO1xuY29uc3QgcmVhY3RfMSA9IHJlcXVpcmUoXCJAcmVtb3RlLXVpL3JlYWN0XCIpO1xuY29uc3QgdmVyc2lvbl8xID0gcmVxdWlyZShcIi4uL3ZlcnNpb25cIik7XG5jb25zdCB3aXRoU2RrUHJvcHMgPSAoQ29tcG9uZW50KSA9PiB7XG4gICAgY29uc3Qgd3JhcHBlZENvbXBvbmVudE5hbWUgPSBDb21wb25lbnQuZGlzcGxheU5hbWUgfHwgQ29tcG9uZW50LnRvU3RyaW5nKCk7XG4gICAgY29uc3QgV2l0aFNka1Byb3BzID0gKHByb3BzKSA9PiAoKDAsIGpzeF9ydW50aW1lXzEuanN4KShDb21wb25lbnQsIHsgLi4ucHJvcHMsIHdyYXBwZWRDb21wb25lbnROYW1lOiB3cmFwcGVkQ29tcG9uZW50TmFtZSwgc2RrVmVyc2lvbjogdmVyc2lvbl8xLlNES19WRVJTSU9OLCBzY2hlbWFWZXJzaW9uOiBcInY5XCIgfSkpO1xuICAgIFdpdGhTZGtQcm9wcy53cmFwcGVkQ29tcG9uZW50TmFtZSA9IHdyYXBwZWRDb21wb25lbnROYW1lO1xuICAgIHJldHVybiBXaXRoU2RrUHJvcHM7XG59O1xuY29uc3QgZGVmaW5lQ29tcG9uZW50ID0gKG5hbWUsIGZyYWdtZW50UHJvcHMsIHdyYXBXaXRoU2RrUHJvcHMpID0+IHtcbiAgICBjb25zdCByZW1vdGVDb21wb25lbnQgPSAoMCwgcmVhY3RfMS5jcmVhdGVSZW1vdGVSZWFjdENvbXBvbmVudCkobmFtZSwge1xuICAgICAgICBmcmFnbWVudFByb3BzLFxuICAgIH0pO1xuICAgIGlmICghd3JhcFdpdGhTZGtQcm9wcykge1xuICAgICAgICByZXR1cm4gcmVtb3RlQ29tcG9uZW50O1xuICAgIH1cbiAgICByZXR1cm4gd2l0aFNka1Byb3BzKHJlbW90ZUNvbXBvbmVudCk7XG59O1xuZXhwb3J0cy5BY2NvcmRpb25JdGVtID0gZGVmaW5lQ29tcG9uZW50KCdBY2NvcmRpb25JdGVtJywgWyd0aXRsZScsICdhY3Rpb25zJywgJ21lZGlhJywgJ3N1YnRpdGxlJ10sIHRydWUpO1xuZXhwb3J0cy5BY2NvcmRpb24gPSBkZWZpbmVDb21wb25lbnQoJ0FjY29yZGlvbicsIFtdLCB0cnVlKTtcbmV4cG9ydHMuQmFkZ2UgPSBkZWZpbmVDb21wb25lbnQoJ0JhZGdlJywgW10sIHRydWUpO1xuZXhwb3J0cy5CYW5uZXIgPSBkZWZpbmVDb21wb25lbnQoJ0Jhbm5lcicsIFsnYWN0aW9ucycsICdkZXNjcmlwdGlvbicsICd0aXRsZSddLCB0cnVlKTtcbmV4cG9ydHMuQmFyQ2hhcnQgPSBkZWZpbmVDb21wb25lbnQoJ0JhckNoYXJ0JywgW10sIHRydWUpO1xuZXhwb3J0cy5Cb3ggPSBkZWZpbmVDb21wb25lbnQoJ0JveCcsIFtdLCB0cnVlKTtcbmV4cG9ydHMuQnV0dG9uR3JvdXAgPSBkZWZpbmVDb21wb25lbnQoJ0J1dHRvbkdyb3VwJywgWydtZW51VHJpZ2dlciddLCB0cnVlKTtcbmV4cG9ydHMuQnV0dG9uID0gZGVmaW5lQ29tcG9uZW50KCdCdXR0b24nLCBbXSwgdHJ1ZSk7XG5leHBvcnRzLkNoZWNrYm94ID0gZGVmaW5lQ29tcG9uZW50KCdDaGVja2JveCcsIFsnbGFiZWwnXSwgdHJ1ZSk7XG5leHBvcnRzLkNoaXBMaXN0ID0gZGVmaW5lQ29tcG9uZW50KCdDaGlwTGlzdCcsIFtdLCB0cnVlKTtcbmV4cG9ydHMuQ2hpcCA9IGRlZmluZUNvbXBvbmVudCgnQ2hpcCcsIFtdLCB0cnVlKTtcbmV4cG9ydHMuQ29udGV4dFZpZXcgPSBkZWZpbmVDb21wb25lbnQoJ0NvbnRleHRWaWV3JywgWydhY3Rpb25zJywgJ2Jhbm5lcicsICdmb290ZXJDb250ZW50JywgJ3ByaW1hcnlBY3Rpb24nLCAnc2Vjb25kYXJ5QWN0aW9uJ10sIHRydWUpO1xuZXhwb3J0cy5EYXRlRmllbGQgPSBkZWZpbmVDb21wb25lbnQoJ0RhdGVGaWVsZCcsIFsnbGFiZWwnXSwgdHJ1ZSk7XG5leHBvcnRzLkRldGFpbFBhZ2VNb2R1bGUgPSBkZWZpbmVDb21wb25lbnQoJ0RldGFpbFBhZ2VNb2R1bGUnLCBbXSwgdHJ1ZSk7XG5leHBvcnRzLkRldGFpbFBhZ2VQcm9wZXJ0eUxpc3QgPSBkZWZpbmVDb21wb25lbnQoJ0RldGFpbFBhZ2VQcm9wZXJ0eUxpc3QnLCBbXSwgdHJ1ZSk7XG5leHBvcnRzLkRldGFpbFBhZ2VUYWJsZSA9IGRlZmluZUNvbXBvbmVudCgnRGV0YWlsUGFnZVRhYmxlJywgW10sIHRydWUpO1xuZXhwb3J0cy5EaXZpZGVyID0gZGVmaW5lQ29tcG9uZW50KCdEaXZpZGVyJywgW10sIHRydWUpO1xuZXhwb3J0cy5Gb2N1c1ZpZXcgPSBkZWZpbmVDb21wb25lbnQoJ0ZvY3VzVmlldycsIFsnZm9vdGVyQ29udGVudCcsICdwcmltYXJ5QWN0aW9uJywgJ3NlY29uZGFyeUFjdGlvbiddLCB0cnVlKTtcbmV4cG9ydHMuRm9ybUZpZWxkR3JvdXAgPSBkZWZpbmVDb21wb25lbnQoJ0Zvcm1GaWVsZEdyb3VwJywgW10sIHRydWUpO1xuZXhwb3J0cy5JY29uID0gZGVmaW5lQ29tcG9uZW50KCdJY29uJywgW10sIHRydWUpO1xuZXhwb3J0cy5JbWcgPSBkZWZpbmVDb21wb25lbnQoJ0ltZycsIFtdLCB0cnVlKTtcbmV4cG9ydHMuSW5saW5lID0gZGVmaW5lQ29tcG9uZW50KCdJbmxpbmUnLCBbXSwgdHJ1ZSk7XG5leHBvcnRzLkxpbmVDaGFydCA9IGRlZmluZUNvbXBvbmVudCgnTGluZUNoYXJ0JywgW10sIHRydWUpO1xuZXhwb3J0cy5MaW5rID0gZGVmaW5lQ29tcG9uZW50KCdMaW5rJywgW10sIHRydWUpO1xuZXhwb3J0cy5MaXN0SXRlbSA9IGRlZmluZUNvbXBvbmVudCgnTGlzdEl0ZW0nLCBbJ2ljb24nLCAnaW1hZ2UnLCAnc2Vjb25kYXJ5VGl0bGUnLCAndGl0bGUnLCAndmFsdWUnXSwgdHJ1ZSk7XG5leHBvcnRzLkxpc3QgPSBkZWZpbmVDb21wb25lbnQoJ0xpc3QnLCBbXSwgdHJ1ZSk7XG5leHBvcnRzLk1lbnVHcm91cCA9IGRlZmluZUNvbXBvbmVudCgnTWVudUdyb3VwJywgWyd0aXRsZSddLCB0cnVlKTtcbmV4cG9ydHMuTWVudUl0ZW0gPSBkZWZpbmVDb21wb25lbnQoJ01lbnVJdGVtJywgW10sIHRydWUpO1xuZXhwb3J0cy5NZW51ID0gZGVmaW5lQ29tcG9uZW50KCdNZW51JywgWyd0cmlnZ2VyJ10sIHRydWUpO1xuZXhwb3J0cy5PbmJvYXJkaW5nVmlldyA9IGRlZmluZUNvbXBvbmVudCgnT25ib2FyZGluZ1ZpZXcnLCBbJ2Vycm9yJ10sIHRydWUpO1xuZXhwb3J0cy5QbGF0Zm9ybUNvbmZpZ3VyYXRpb25WaWV3ID0gZGVmaW5lQ29tcG9uZW50KCdQbGF0Zm9ybUNvbmZpZ3VyYXRpb25WaWV3JywgW10sIHRydWUpO1xuZXhwb3J0cy5Qcm9wZXJ0eUxpc3RJdGVtID0gZGVmaW5lQ29tcG9uZW50KCdQcm9wZXJ0eUxpc3RJdGVtJywgWydsYWJlbCcsICd2YWx1ZSddLCB0cnVlKTtcbmV4cG9ydHMuUHJvcGVydHlMaXN0ID0gZGVmaW5lQ29tcG9uZW50KCdQcm9wZXJ0eUxpc3QnLCBbXSwgdHJ1ZSk7XG5leHBvcnRzLlJhZGlvID0gZGVmaW5lQ29tcG9uZW50KCdSYWRpbycsIFsnbGFiZWwnXSwgdHJ1ZSk7XG5leHBvcnRzLlNlbGVjdCA9IGRlZmluZUNvbXBvbmVudCgnU2VsZWN0JywgWydsYWJlbCddLCB0cnVlKTtcbmV4cG9ydHMuU2V0dGluZ3NWaWV3ID0gZGVmaW5lQ29tcG9uZW50KCdTZXR0aW5nc1ZpZXcnLCBbXSwgdHJ1ZSk7XG5leHBvcnRzLlNpZ25JblZpZXcgPSBkZWZpbmVDb21wb25lbnQoJ1NpZ25JblZpZXcnLCBbJ2Rlc2NyaXB0aW9uQWN0aW9uQ29udGVudHMnLCAnZm9vdGVyQ29udGVudCddLCB0cnVlKTtcbmV4cG9ydHMuU3BhcmtsaW5lID0gZGVmaW5lQ29tcG9uZW50KCdTcGFya2xpbmUnLCBbXSwgdHJ1ZSk7XG5leHBvcnRzLlNwaW5uZXIgPSBkZWZpbmVDb21wb25lbnQoJ1NwaW5uZXInLCBbXSwgdHJ1ZSk7XG5leHBvcnRzLlN0cmlwZUZpbGVVcGxvYWRlciA9IGRlZmluZUNvbXBvbmVudCgnU3RyaXBlRmlsZVVwbG9hZGVyJywgW10sIHRydWUpO1xuZXhwb3J0cy5Td2l0Y2ggPSBkZWZpbmVDb21wb25lbnQoJ1N3aXRjaCcsIFsnbGFiZWwnXSwgdHJ1ZSk7XG5leHBvcnRzLlRhYkxpc3QgPSBkZWZpbmVDb21wb25lbnQoJ1RhYkxpc3QnLCBbXSwgdHJ1ZSk7XG5leHBvcnRzLlRhYlBhbmVsID0gZGVmaW5lQ29tcG9uZW50KCdUYWJQYW5lbCcsIFtdLCB0cnVlKTtcbmV4cG9ydHMuVGFiUGFuZWxzID0gZGVmaW5lQ29tcG9uZW50KCdUYWJQYW5lbHMnLCBbXSwgdHJ1ZSk7XG5leHBvcnRzLlRhYiA9IGRlZmluZUNvbXBvbmVudCgnVGFiJywgW10sIHRydWUpO1xuZXhwb3J0cy5UYWJsZUJvZHkgPSBkZWZpbmVDb21wb25lbnQoJ1RhYmxlQm9keScsIFtdLCB0cnVlKTtcbmV4cG9ydHMuVGFibGVDZWxsID0gZGVmaW5lQ29tcG9uZW50KCdUYWJsZUNlbGwnLCBbXSwgdHJ1ZSk7XG5leHBvcnRzLlRhYmxlRm9vdGVyID0gZGVmaW5lQ29tcG9uZW50KCdUYWJsZUZvb3RlcicsIFtdLCB0cnVlKTtcbmV4cG9ydHMuVGFibGVIZWFkID0gZGVmaW5lQ29tcG9uZW50KCdUYWJsZUhlYWQnLCBbXSwgdHJ1ZSk7XG5leHBvcnRzLlRhYmxlSGVhZGVyQ2VsbCA9IGRlZmluZUNvbXBvbmVudCgnVGFibGVIZWFkZXJDZWxsJywgW10sIHRydWUpO1xuZXhwb3J0cy5UYWJsZSA9IGRlZmluZUNvbXBvbmVudCgnVGFibGUnLCBbXSwgdHJ1ZSk7XG5leHBvcnRzLlRhYmxlUm93ID0gZGVmaW5lQ29tcG9uZW50KCdUYWJsZVJvdycsIFtdLCB0cnVlKTtcbmV4cG9ydHMuVGFicyA9IGRlZmluZUNvbXBvbmVudCgnVGFicycsIFtdLCB0cnVlKTtcbmV4cG9ydHMuVGFza0xpc3RJdGVtID0gZGVmaW5lQ29tcG9uZW50KCdUYXNrTGlzdEl0ZW0nLCBbXSwgdHJ1ZSk7XG5leHBvcnRzLlRhc2tMaXN0ID0gZGVmaW5lQ29tcG9uZW50KCdUYXNrTGlzdCcsIFtdLCB0cnVlKTtcbmV4cG9ydHMuVGV4dEFyZWEgPSBkZWZpbmVDb21wb25lbnQoJ1RleHRBcmVhJywgWydsYWJlbCddLCB0cnVlKTtcbmV4cG9ydHMuVGV4dEZpZWxkID0gZGVmaW5lQ29tcG9uZW50KCdUZXh0RmllbGQnLCBbJ2xhYmVsJ10sIHRydWUpO1xuZXhwb3J0cy5Ub29sdGlwID0gZGVmaW5lQ29tcG9uZW50KCdUb29sdGlwJywgWyd0cmlnZ2VyJ10sIHRydWUpO1xuIiwgIi8vIEFVVE9HRU5FUkFURUQgLSBETyBOT1QgTU9ESUZZXG5cbi8vIFZpZXcgY29tcG9uZW50IGltcG9ydHMgXHUyMDE0IG9uZSBwZXIgdmlld3BvcnQgZGVjbGFyZWQgaW4gdWlfZXh0ZW5zaW9uLnZpZXdzXG5pbXBvcnQgQXBwVmlldyBmcm9tICcuLi9zcmMvdmlld3MvQXBwVmlldyc7XG5cbi8vIEV4cG9zZXMgdGhlIFNESyB2ZXJzaW9uIHNvIHRoZSBEYXNoYm9hcmQgY2FuIHZlcmlmeSBjb21wYXRpYmlsaXR5XG5leHBvcnQgKiBmcm9tICdAc3RyaXBlL3VpLWV4dGVuc2lvbi1zZGsvdmVyc2lvbic7XG5cbi8vIE5hbWVkIGV4cG9ydHMgbWFrZSBlYWNoIHZpZXcgY29tcG9uZW50IGFjY2Vzc2libGUgdG8gdGhlIERhc2hib2FyZCBydW50aW1lXG5cbmV4cG9ydCB7IFxuICBBcHBWaWV3XG4gfTtcblxuLy8gVGltZXN0YW1wIGNoYW5nZXMgb24gZXZlcnkgZXhwb3J0LCBlbnN1cmluZyB0aGUgZGV2IHNlcnZlciBkZXRlY3RzIGEgcmVidWlsZFxuZXhwb3J0IGNvbnN0IEJVSUxEX1RJTUUgPSAnMjAyNi0wNi0yNiAyMToyMDo0Ni42ODM5MjEyIC0wMzAwIC0wMyBtPSszLjMxOTgwNTUwMSc7XG5cbi8vIEFwcCBtYW5pZmVzdCBcdTIwMTQgY29uc3VtZWQgYnkgdGhlIERhc2hib2FyZCB0byBjb25maWd1cmUgdGhlIGFwcFxuZXhwb3J0IGRlZmF1bHQge1xuICBcIiRzY2hlbWFcIjogXCJodHRwczovL3N0cmlwZS5jb20vc3RyaXBlLWFwcC5zY2hlbWEuanNvblwiLFxuICBcImRpc3RyaWJ1dGlvbl90eXBlXCI6IFwicHVibGljXCIsXG4gIFwiaWNvblwiOiBcIi4vcHVibGljL2ljb24ucG5nXCIsXG4gIFwiaWRcIjogXCJjb20uZ2xvYmFsZW5nZW5oYXJpYS5lY29zeXN0ZW0tY29tcGxpYW5jZVwiLFxuICBcIm5hbWVcIjogXCJFY29TeXN0ZW0gQ29tcGxpYW5jZVwiLFxuICBcInBlcm1pc3Npb25zXCI6IFtcbiAgICB7XG4gICAgICBcInBlcm1pc3Npb25cIjogXCJjdXN0b21lcl9yZWFkXCIsXG4gICAgICBcInB1cnBvc2VcIjogXCJJZGVudGlmaWNhciBlbXByZXNhIHBhcmEgZ2VyYXIgc2NvcmUgZGUgY29tcGxpYW5jZVwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInBlcm1pc3Npb25cIjogXCJpbnZvaWNlX3JlYWRcIixcbiAgICAgIFwicHVycG9zZVwiOiBcIlZlcmlmaWNhciB2b2x1bWUgZGUgdHJhbnNhY29lcyBwYXJhIHJlY29tZW5kYXIgYWdlbnRlc1wiXG4gICAgfVxuICBdLFxuICBcInVpX2V4dGVuc2lvblwiOiB7XG4gICAgXCJjb250ZW50X3NlY3VyaXR5X3BvbGljeVwiOiB7XG4gICAgICBcImNvbm5lY3Qtc3JjXCI6IFtcbiAgICAgICAgXCJodHRwczovL2VuZ2VuaGVpcm8tcHJvZHVjYW8tYWkub25yZW5kZXIuY29tL2FwaS9zdHJpcGUvY29tcGxpYW5jZS1zY29yZVwiXG4gICAgICBdLFxuICAgICAgXCJwdXJwb3NlXCI6IFwiQ29uZWN0YXIgYW8gRWNvU3lzdGVtIEFQSSBwYXJhIGdlcmFyIHNjb3JlIGRlIGNvbXBsaWFuY2VcIlxuICAgIH0sXG4gICAgXCJ2aWV3c1wiOiBbXG4gICAgICB7XG4gICAgICAgIFwiY29tcG9uZW50XCI6IFwiQXBwVmlld1wiLFxuICAgICAgICBcInZpZXdwb3J0XCI6IFwic3RyaXBlLmRhc2hib2FyZC5ob21lLm92ZXJ2aWV3XCJcbiAgICAgIH1cbiAgICBdXG4gIH0sXG4gIFwidmVyc2lvblwiOiBcIjEuMC4wXCJcbn07XG4iLCAiaW1wb3J0IHsgQm94LCBCdXR0b24sIENvbnRleHRWaWV3LCBEaXZpZGVyLCBCYWRnZSwgSW5saW5lLCBMaW5rLCBMaXN0LCBMaXN0SXRlbSwgU3Bpbm5lciwgVGV4dCwgQmFubmVyIH0gZnJvbSBcIkBzdHJpcGUvdWktZXh0ZW5zaW9uLXNkay91aVwiO1xuaW1wb3J0IHR5cGUgeyBFeHRlbnNpb25Db250ZXh0VmFsdWUgfSBmcm9tIFwiQHN0cmlwZS91aS1leHRlbnNpb24tc2RrL2NvbnRleHRcIjtcbmltcG9ydCB7IHVzZUVmZmVjdCwgdXNlU3RhdGUgfSBmcm9tIFwicmVhY3RcIjtcblxuY29uc3QgQVBJX1VSTCA9IFwiaHR0cHM6Ly9lbmdlbmhlaXJvLXByb2R1Y2FvLWFpLm9ucmVuZGVyLmNvbVwiO1xuXG5pbnRlcmZhY2UgQ29tcGxpYW5jZVNjb3JlIHtcbiAgc2NvcmU6IG51bWJlcjtcbiAgbml2ZWw6IHN0cmluZztcbiAgb2JyaWdhY29lczogeyBub21lOiBzdHJpbmc7IHN0YXR1czogc3RyaW5nOyBwcmF6bz86IHN0cmluZzsgbXVsdGE/OiBzdHJpbmcgfVtdO1xuICBwbGFub19yZWNvbWVuZGFkbzogc3RyaW5nO1xuICBsaW5rX2F0aXZhY2FvOiBzdHJpbmc7XG59XG5cbmNvbnN0IEVjb3N5c3RlbUFwcCA9ICh7IHVzZXJDb250ZXh0IH06IEV4dGVuc2lvbkNvbnRleHRWYWx1ZSkgPT4ge1xuICBjb25zdCBbc2NvcmUsIHNldFNjb3JlXSA9IHVzZVN0YXRlPENvbXBsaWFuY2VTY29yZSB8IG51bGw+KG51bGwpO1xuICBjb25zdCBbbG9hZGluZywgc2V0TG9hZGluZ10gPSB1c2VTdGF0ZSh0cnVlKTtcbiAgY29uc3QgW2Vycm9yLCBzZXRFcnJvcl0gPSB1c2VTdGF0ZTxzdHJpbmcgfCBudWxsPihudWxsKTtcblxuICB1c2VFZmZlY3QoKCkgPT4ge1xuICAgIGZldGNoQ29tcGxpYW5jZVNjb3JlKCk7XG4gIH0sIFtdKTtcblxuICBjb25zdCBmZXRjaENvbXBsaWFuY2VTY29yZSA9IGFzeW5jICgpID0+IHtcbiAgICB0cnkge1xuICAgICAgY29uc3QgcmVzcG9uc2UgPSBhd2FpdCBmZXRjaChgJHtBUElfVVJMfS9hcGkvc3RyaXBlL2NvbXBsaWFuY2Utc2NvcmVgLCB7XG4gICAgICAgIG1ldGhvZDogXCJQT1NUXCIsXG4gICAgICAgIGhlYWRlcnM6IHsgXCJDb250ZW50LVR5cGVcIjogXCJhcHBsaWNhdGlvbi9qc29uXCIgfSxcbiAgICAgICAgYm9keTogSlNPTi5zdHJpbmdpZnkoeyBzdHJpcGVfYWNjb3VudF9pZDogdXNlckNvbnRleHQ/LmFjY291bnQ/LmlkLCBlbWFpbDogdXNlckNvbnRleHQ/LmFjY291bnQ/LmVtYWlsIH0pLFxuICAgICAgfSk7XG4gICAgICBjb25zdCBkYXRhID0gYXdhaXQgcmVzcG9uc2UuanNvbigpO1xuICAgICAgc2V0U2NvcmUoZGF0YSk7XG4gICAgfSBjYXRjaCB7XG4gICAgICBzZXRFcnJvcihcIk5cdTAwRTNvIGZvaSBwb3NzXHUwMEVEdmVsIGNhcnJlZ2FyIG8gc2NvcmUuXCIpO1xuICAgIH0gZmluYWxseSB7XG4gICAgICBzZXRMb2FkaW5nKGZhbHNlKTtcbiAgICB9XG4gIH07XG5cbiAgY29uc3QgZ2V0U2NvcmVDb2xvciA9IChzOiBudW1iZXIpID0+IChzID49IDgwID8gXCJzdWNjZXNzXCIgOiBzID49IDUwID8gXCJ3YXJuaW5nXCIgOiBcImNyaXRpY2FsXCIpO1xuXG4gIGlmIChsb2FkaW5nKSByZXR1cm4gKFxuICAgIDxDb250ZXh0VmlldyB0aXRsZT1cIkVjb1N5c3RlbSBDb21wbGlhbmNlXCI+XG4gICAgICA8Qm94IGNzcz17eyBzdGFjazogXCJ4XCIsIGdhcDogXCJtZWRpdW1cIiwgYWxpZ25ZOiBcImNlbnRlclwiIH19PlxuICAgICAgICA8U3Bpbm5lciAvPlxuICAgICAgICA8VGV4dD5BbmFsaXNhbmRvIGNvbXBsaWFuY2UgZGEgc3VhIGVtcHJlc2EuLi48L1RleHQ+XG4gICAgICA8L0JveD5cbiAgICA8L0NvbnRleHRWaWV3PlxuICApO1xuXG4gIGlmIChlcnJvcikgcmV0dXJuIChcbiAgICA8Q29udGV4dFZpZXcgdGl0bGU9XCJFY29TeXN0ZW0gQ29tcGxpYW5jZVwiPlxuICAgICAgPEJhbm5lciB0eXBlPVwiY3JpdGljYWxcIiB0aXRsZT1cIkVycm9cIiBkZXNjcmlwdGlvbj17ZXJyb3J9IC8+XG4gICAgPC9Db250ZXh0Vmlldz5cbiAgKTtcblxuICByZXR1cm4gKFxuICAgIDxDb250ZXh0VmlldyB0aXRsZT1cIkVjb1N5c3RlbSBDb21wbGlhbmNlXCIgZGVzY3JpcHRpb249XCJTY29yZSBkZSBjb21wbGlhbmNlIHJlZ3VsYXRcdTAwRjNyaW8gZGEgc3VhIGVtcHJlc2FcIj5cbiAgICAgIDxCb3ggY3NzPXt7IHBhZGRpbmc6IFwibGFyZ2VcIiwgYmFja2dyb3VuZDogXCJjb250YWluZXJcIiwgYm9yZGVyUmFkaXVzOiBcIm1lZGl1bVwiLCBtYXJnaW5Cb3R0b206IFwibWVkaXVtXCIgfX0+XG4gICAgICAgIDxUZXh0IHNpemU9XCJzbWFsbFwiIGNvbG9yPVwic2Vjb25kYXJ5XCI+U2NvcmUgZGUgQ29tcGxpYW5jZTwvVGV4dD5cbiAgICAgICAgPEJveCBjc3M9e3sgc3RhY2s6IFwieFwiLCBhbGlnblk6IFwiY2VudGVyXCIsIGdhcDogXCJzbWFsbFwiLCBtYXJnaW5Ub3A6IFwic21hbGxcIiB9fT5cbiAgICAgICAgICA8VGV4dCBzaXplPVwieHhsYXJnZVwiIHdlaWdodD1cImJvbGRcIiBjb2xvcj17Z2V0U2NvcmVDb2xvcihzY29yZT8uc2NvcmUgfHwgMCl9PntzY29yZT8uc2NvcmUgfHwgMH08L1RleHQ+XG4gICAgICAgICAgPFRleHQgc2l6ZT1cInhsYXJnZVwiIGNvbG9yPVwic2Vjb25kYXJ5XCI+LzEwMDwvVGV4dD5cbiAgICAgICAgICA8QmFkZ2UgdHlwZT17Z2V0U2NvcmVDb2xvcihzY29yZT8uc2NvcmUgfHwgMCkgYXMgYW55fT57c2NvcmU/Lm5pdmVsfTwvQmFkZ2U+XG4gICAgICAgIDwvQm94PlxuICAgICAgPC9Cb3g+XG4gICAgICA8RGl2aWRlciAvPlxuICAgICAgPEJveCBjc3M9e3sgbWFyZ2luVG9wOiBcIm1lZGl1bVwiLCBtYXJnaW5Cb3R0b206IFwibWVkaXVtXCIgfX0+XG4gICAgICAgIDxUZXh0IHdlaWdodD1cInNlbWlib2xkXCIgc2l6ZT1cInNtYWxsXCI+T2JyaWdhXHUwMEU3XHUwMEY1ZXMgUmVndWxhdFx1MDBGM3JpYXM8L1RleHQ+XG4gICAgICAgIDxMaXN0PlxuICAgICAgICAgIHtzY29yZT8ub2JyaWdhY29lcy5tYXAoKG9iLCBpKSA9PiAoXG4gICAgICAgICAgICA8TGlzdEl0ZW0ga2V5PXtpfSB0aXRsZT17b2Iubm9tZX0gdmFsdWU9ezxCYWRnZSB0eXBlPXtvYi5zdGF0dXMgPT09IFwib2tcIiA/IFwic3VjY2Vzc1wiIDogXCJjcml0aWNhbFwifT57b2Iuc3RhdHVzID09PSBcIm9rXCIgPyBcIkVtIGRpYVwiIDogXCJDclx1MDBFRHRpY29cIn08L0JhZGdlPn0gLz5cbiAgICAgICAgICApKX1cbiAgICAgICAgPC9MaXN0PlxuICAgICAgPC9Cb3g+XG4gICAgICA8RGl2aWRlciAvPlxuICAgICAge3Njb3JlPy5zY29yZSAmJiBzY29yZS5zY29yZSA8IDEwMCAmJiAoXG4gICAgICAgIDxCb3ggY3NzPXt7IG1hcmdpblRvcDogXCJtZWRpdW1cIiB9fT5cbiAgICAgICAgICA8QmFubmVyIHR5cGU9XCJ3YXJuaW5nXCIgdGl0bGU9e2BQbGFubyByZWNvbWVuZGFkbzogJHtzY29yZS5wbGFub19yZWNvbWVuZGFkb31gfSBkZXNjcmlwdGlvbj1cIlJlZ3VsYXJpemUgc3VhIGVtcHJlc2EgZW0gNDhoIGNvbSBub3Nzb3MgYWdlbnRlcyBkZSBJQVwiIC8+XG4gICAgICAgICAgPEJveCBjc3M9e3sgbWFyZ2luVG9wOiBcInNtYWxsXCIgfX0+XG4gICAgICAgICAgICA8QnV0dG9uIHR5cGU9XCJwcmltYXJ5XCIgaHJlZj17c2NvcmUubGlua19hdGl2YWNhb30gdGFyZ2V0PVwiX2JsYW5rXCI+QXRpdmFyIGFnZW50ZXMgZGUgY29tcGxpYW5jZSBcdTIxOTI8L0J1dHRvbj5cbiAgICAgICAgICA8L0JveD5cbiAgICAgICAgPC9Cb3g+XG4gICAgICApfVxuICAgICAgPEJveCBjc3M9e3sgbWFyZ2luVG9wOiBcIm1lZGl1bVwiIH19PlxuICAgICAgICA8VGV4dCBzaXplPVwieHNtYWxsXCIgY29sb3I9XCJzZWNvbmRhcnlcIj5Qb3dlcmVkIGJ5IEVjb1N5c3RlbSBBSSBcdTIwMTQgR2xvYmFsIE1hdGNoIEVuZ2VuaGFyaWE8L1RleHQ+XG4gICAgICA8L0JveD5cbiAgICA8L0NvbnRleHRWaWV3PlxuICApO1xufTtcblxuZXhwb3J0IGRlZmF1bHQgRWNvc3lzdGVtQXBwO1xuIl0sCiAgIm1hcHBpbmdzIjogIjs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7QUFBQTtBQUFBO0FBQUE7QUFDQSxhQUFPLGVBQWUsU0FBUyxjQUFjLEVBQUUsT0FBTyxLQUFLLENBQUM7QUFDNUQsY0FBUSxjQUFjO0FBQ3RCLGNBQVEsY0FBYztBQUFBO0FBQUE7OztBQ0h0QjtBQUFBO0FBQUE7QUFDQSxhQUFPLGVBQWUsU0FBUyxjQUFjLEVBQUUsT0FBTyxLQUFLLENBQUM7QUFDNUQsY0FBUSxrQkFBa0IsUUFBUSxZQUFZLFFBQVEsY0FBYyxRQUFRLFlBQVksUUFBUSxZQUFZLFFBQVEsTUFBTSxRQUFRLFlBQVksUUFBUSxXQUFXLFFBQVEsVUFBVSxRQUFRLFNBQVMsUUFBUSxxQkFBcUIsUUFBUSxVQUFVLFFBQVEsWUFBWSxRQUFRLGFBQWEsUUFBUSxlQUFlLFFBQVEsU0FBUyxRQUFRLFFBQVEsUUFBUSxlQUFlLFFBQVEsbUJBQW1CLFFBQVEsNEJBQTRCLFFBQVEsaUJBQWlCLFFBQVEsT0FBTyxRQUFRLFdBQVcsUUFBUSxZQUFZLFFBQVEsT0FBTyxRQUFRLFdBQVcsUUFBUSxPQUFPLFFBQVEsWUFBWSxRQUFRLFNBQVMsUUFBUSxNQUFNLFFBQVEsT0FBTyxRQUFRLGlCQUFpQixRQUFRLFlBQVksUUFBUSxVQUFVLFFBQVEsa0JBQWtCLFFBQVEseUJBQXlCLFFBQVEsbUJBQW1CLFFBQVEsWUFBWSxRQUFRLGNBQWMsUUFBUSxPQUFP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
