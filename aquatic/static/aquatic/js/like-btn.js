      const likeButtons = document.querySelectorAll(".like-btn");

      likeButtons.forEach((button) => {
        button.addEventListener("click", function () {
          this.classList.toggle("liked"); // 切換 class
          console.log("愛心切換成功！"); // 可以在 F12 console 看到這行字
        });
      });