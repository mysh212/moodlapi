# MoodlAPI

An API to access (NCKU) Moodle without a mouse just like CLI

## Inspiration

### Verification code

Hmm, the NCKU Moodle just introduced a new login method, with VERIFICATION CODE (???????
This means you HAVE TO type for at least 20 seconds each time you try to login to Moodle

And if you login to Moodle twice a day, this means you'll waste about 

$$
\frac{20}{60} \times 365 = 121.\bar{6} \text{ minutes}
$$

per year, you can write 10 more lines of code using this time you wasted.

So I decided to write a project to solve this.

 - [Reference - Redesigned Frontend for Moodle](https://github.com/mysh212/toolbox-frontend)

### Notification

And the other reason I'm doing this is that Moodle doesn't actually send you notifications each time the teachers have made changes.

> ~~Hmm, the actual reason is simply that I want to use my terminal to access Moodle so I can show off like I were a hacker.~~

---

## Usage

Just clone it and use `uv` to synchronize the environment.

```
uv sync
```

And you can simply import this module and embed it into your project:D
