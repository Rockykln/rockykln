```rust
//! github.com/Rockykln

pub struct Developer {
    pub handle: &'static str,
    pub place: &'static str,
    pub rule: &'static str,
    pub learning: &'static [&'static str],
}

pub const ME: Developer = Developer {
    handle: "rockykln",
    place: "Germany",
    rule: "one tool, one annoyance, finished",
    learning: &["kernel modules", "DRM", "V4L2"],
};

pub struct Project {
    pub name: &'static str,
    pub problem: &'static str,
    pub answer: &'static str,
    pub built_with: &'static [&'static str],
    pub install: Option<&'static str>,
    pub home: &'static str,
    pub state: State,
    pub stars: u32,
    pub last_push: Days,
}

pub enum State {
    Shipping(&'static str),
    InDevelopment,
}

pub struct Days(pub u32);

// DATA:BEGIN
pub const PORTFOLIO: [Project; 5] = [
    Project {
        name: "LocSim",
        problem: "an iPhone cannot pretend to be elsewhere without a Mac attached",
        answer: "ask the phone's own developer services, from the phone",
        built_with: &["Swift", "RemoteXPC", "DVT", "packet tunnel"],
        install: None,
        home: "locsim.rockykln.com",
        state: State::InDevelopment,
        stars: 19,
        last_push: Days(0),
    },
    Project {
        name: "Refrain",
        problem: "Apple Music has no Linux app, so Discord never sees the song",
        answer: "read the browser or a phone over Bluetooth, post it with cover art",
        built_with: &["Python", "MPRIS", "Last.fm", "10 languages"],
        install: Some("yay -S refrain"),
        home: "refrain.rockykln.com",
        state: State::Shipping("v0.5.6"),
        stars: 3,
        last_push: Days(2),
    },
    Project {
        name: "podctl",
        problem: "AirPods hide half their settings, and all of Linux",
        answer: "speak the Apple Accessory Protocol over L2CAP, written from scratch",
        built_with: &["Rust", "L2CAP", "PipeWire", "BlueZ"],
        install: Some("yay -S podctl-bin"),
        home: "podctl.rockykln.com",
        state: State::Shipping("v0.4.0"),
        stars: 12,
        last_push: Days(1),
    },
    Project {
        name: "nettools",
        problem: "a DNS lookup online costs three ads and a cookie banner",
        answer: "render on the server, share by link, open the same data as an API",
        built_with: &["TypeScript", "Cloudflare Workers", "no JavaScript needed"],
        install: None,
        home: "net.rockykln.com",
        state: State::Shipping("v0.1.1"),
        stars: 2,
        last_push: Days(0),
    },
    Project {
        name: "clientctl",
        problem: "a desktop is unreachable the moment you leave the desk",
        answer: "drive apps, audio and displays from any browser, behind passkeys",
        built_with: &["Python", "WebAuthn", "KDE Plasma 6"],
        install: None,
        home: "clientctl.rockykln.com",
        state: State::Shipping("v0.1.1"),
        stars: 0,
        last_push: Days(4),
    },
];
// DATA:END

pub struct Platform {
    pub name: &'static str,
    pub since: u32,
    pub services: &'static [(&'static str, &'static str)],
    pub hosted_on: &'static str,
}

/// Not a project
pub const KEY64: Platform = Platform {
    name: "key64",
    since: 2024,
    services: &[
        ("discord bot", "quests, music, moderation for my own server"),
        ("dashboard", "one place to see and drive all of it"),
        ("status page", "uptime of every service, public"),
        ("cdn", "static files, hashed names, served from the edge"),
    ],
    hosted_on: "SparkedHost",
};

/// Links that pay me a little if you use them
pub const AFFILIATES: [(&str, &str); 2] = [
    ("SparkedHost", "billing.sparkedhost.com/aff.php?aff=2321"),
    ("Instant Gaming", "instant-gaming.com/?igr=rockykln"),
];

impl Project {
    pub fn is_alive(&self) -> bool {
        self.last_push.0 < 90
    }

    pub fn tracks_users(&self) -> bool {
        false // none of them do
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn every_project_names_the_annoyance_it_removes() {
        assert!(PORTFOLIO.iter().all(|p| !p.problem.is_empty() && !p.answer.is_empty()));
    }

    #[test]
    fn nothing_is_abandoned() {
        assert!(PORTFOLIO.iter().all(Project::is_alive));
    }

    #[test]
    fn the_platform_is_fully_staffed() {
        assert_eq!(KEY64.services.len(), 4);
    }

    #[test]
    fn affiliate_links_are_declared() {
        assert!(AFFILIATES.iter().all(|(name, url)| !name.is_empty() && !url.is_empty()));
    }

    #[test]
    fn no_ads_no_accounts_no_telemetry() {
        assert_eq!(PORTFOLIO.iter().filter(|p| p.tracks_users()).count(), 0);
    }
}

// $ cargo test
// running 5 tests
// .....
// test result: ok. 5 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

<p align="center">
  <a href="https://locsim.rockykln.com"><img src="https://raw.githubusercontent.com/Rockykln/rockykln/output/badge-locsim.svg" alt="LocSim — in development, 19 stars"></a>
  <a href="https://refrain.rockykln.com"><img src="https://raw.githubusercontent.com/Rockykln/rockykln/output/badge-refrain.svg" alt="Refrain — v0.5.6, 3 stars"></a>
  <a href="https://podctl.rockykln.com"><img src="https://raw.githubusercontent.com/Rockykln/rockykln/output/badge-podctl.svg" alt="podctl — v0.4.0, 12 stars"></a>
  <a href="https://net.rockykln.com"><img src="https://raw.githubusercontent.com/Rockykln/rockykln/output/badge-nettools.svg" alt="nettools — v0.1.1, 2 stars"></a>
  <a href="https://clientctl.rockykln.com"><img src="https://raw.githubusercontent.com/Rockykln/rockykln/output/badge-clientctl.svg" alt="clientctl — v0.1.1, 0 stars"></a>
  
  <a href="https://github.com/Rockykln/rockykln/actions"><img src="https://raw.githubusercontent.com/Rockykln/rockykln/output/badge-tests.svg" alt="profile tests: 5 passed"></a>
</p>

[rockykln.com](https://www.rockykln.com) · [contact@rockykln.com](mailto:contact@rockykln.com)

<sub>Hosting by [SparkedHost](https://billing.sparkedhost.com/aff.php?aff=2321) · games from [Instant Gaming](https://www.instant-gaming.com/?igr=rockykln)</sub>
